import re
import json
import datetime
import hashlib
from typing                                                                       import Dict, List, Optional, Tuple
from osbot_utils.type_safe.Type_Safe                                              import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_Int                               import Safe_Int
from osbot_utils.type_safe.primitives.core.Safe_Str                               import Safe_Str
from osbot_utils.type_safe.primitives.domains.common.safe_str.Safe_Str__Version   import Safe_Str__Version
from osbot_utils.type_safe.primitives.domains.files.safe_str.Safe_Str__File__Path import Safe_Str__File__Path


class IR_Server(Type_Safe):
    url        : Safe_Str
    variables  : dict

class IR_Parameter(Type_Safe):
    name       : Safe_Str
    in_        : Safe_Str               # path | query | header | cookie
    required   : bool           = False
    schema     : dict           = None  # raw schema node

class IR_RequestBody(Type_Safe):
    content_types : List[str]
    schema        : dict         = None

class IR_Response(Type_Safe):
    status_code : Safe_Str
    content     : dict = None

class IR_Operation(Type_Safe):
    operation_id : Safe_Str
    method       : Safe_Str
    path         : Safe_Str__File__Path
    tag          : Safe_Str             = None
    summary      : Safe_Str             = None
    parameters   : List[IR_Parameter]
    request_body : IR_RequestBody       = None
    responses    : List[IR_Response]
    deprecated   : bool                 = False
    security     : list                 = None

class IR_Spec(Type_Safe):
    title        : Safe_Str
    version      : Safe_Str__Version    = None
    servers      : List[IR_Server]
    operations   : List[IR_Operation]
    spec_hash    : Safe_Str

class OpenAPI__To__Python(Type_Safe):
    prefer_tag_sections : bool = True                    # group methods by tag as comments
    use_safe_primitives : bool = True                    # future hook for richer type mapping
    class_name_prefix   : Safe_Str = 'Client__'          # final class name is Client__{Service}
    default_timeout_sec : Safe_Int = 30

    # ------------- public API -------------

    def generate_from_json_str(self, json_str: str) -> str:
        spec_dict = json.loads(json_str)
        return self.generate_from_dict(spec_dict)

    def generate_from_app(self, app) -> str:
        """Convenience: accept a FastAPI app instance and use its in-memory OpenAPI."""
        openapi_dict = app.openapi()
        return self.generate_from_dict(openapi_dict)

    def generate_from_dict(self, spec: dict) -> str:
        ir       = self._build_ir(spec)
        content  = self._render_client(ir, raw_spec=spec)
        return content

    # ------------- IR building -------------

    def _build_ir(self, spec: dict) -> IR_Spec:
        title     = Safe_Str         (spec.get('info', {}).get('title', 'Service'))
        version   = Safe_Str__Version(spec.get('info', {}).get('version', '0.0.0'))
        servers   = [IR_Server(url=Safe_Str(s.get('url', '/')), variables=s.get('variables', {}))
                     for s in spec.get('servers', [])] or [IR_Server(url=Safe_Str('/'))]

        # Compute stable hash of normalized spec
        spec_hash = hashlib.sha1(json.dumps(spec, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

        ops: List[IR_Operation] = []
        paths = spec.get('paths', {})
        for path, path_item in paths.items():
            for method in ('get','post','put','delete','patch','head','options','trace'):
                if method not in path_item:
                    continue
                op_node = path_item[method]

                op_id      = self._op_id(path, method, op_node.get('operationId'))
                tag        = (op_node.get('tags') or [None])[0]
                params     = self._collect_parameters(path_item, op_node)
                request_b  = self._collect_request_body(op_node)
                responses  = self._collect_responses(op_node.get('responses', {}))
                deprecated = bool(op_node.get('deprecated', False))
                security   = op_node.get('security')

                ops.append(IR_Operation( operation_id = Safe_Str(op_id)                ,
                                         method       = Safe_Str(method.upper())       ,
                                         path         = Safe_Str__File__Path(path)     ,
                                         tag          = Safe_Str(tag) if tag else None ,
                                         summary      = Safe_Str(op_node.get('summary')) if op_node.get('summary') else None,
                                         parameters   = params                         ,
                                         request_body = request_b                      ,
                                         responses    = responses                      ,
                                         deprecated   = deprecated                     ,
                                         security     = security                       ))

        return IR_Spec(title=title, version=version, servers=servers, operations=ops, spec_hash=Safe_Str(spec_hash))

    def _op_id(self, path: str, method: str, explicit: Optional[str]) -> str:
        path_clean = re.sub(r'[^a-zA-Z0-9]+', '_', path).strip('_')             # Always generate from path, ignore explicit operationId
        name = f"{method.lower()}_{path_clean}"  # get_config_status
        return self._sanitize_method_name(name)

    def _sanitize_method_name(self, name: str) -> str:
        name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        if not re.match(r'[A-Za-z_]', name):
            name = f"op_{name}"
        return re.sub(r'__+', '_', name).lower()

    def _collect_parameters(self, path_item: dict, op_node: dict) -> List[IR_Parameter]:
        all_params = []
        for source in (path_item.get('parameters', []), op_node.get('parameters', [])):
            for p in source:
                all_params.append(IR_Parameter(name=Safe_Str(p.get('name')),
                                               in_=Safe_Str(p.get('in')),
                                               required=bool(p.get('required', False)),
                                               schema=p.get('schema')))
        # Deduplicate by (name, in)
        dedup: Dict[Tuple[str,str], IR_Parameter] = {}
        for p in all_params:
            key = (str(p.name), str(p.in_))
            dedup[key] = p
        return list(dedup.values())

    def _collect_request_body(self, op_node: dict) -> Optional[IR_RequestBody]:
        rb = op_node.get('requestBody')
        if not rb:
            return None
        content = rb.get('content') or {}
        content_types = list(content.keys())
        schema = None
        # Prefer application/json
        if 'application/json' in content:
            schema = content['application/json'].get('schema')
        elif content_types:
            schema = (content[content_types[0]] or {}).get('schema')
        return IR_RequestBody(content_types=content_types, schema=schema)

    def _collect_responses(self, responses: dict) -> List[IR_Response]:
        out: List[IR_Response] = []
        for status, node in responses.items():
            out.append(IR_Response(status_code=Safe_Str(status), content=node.get('content')))
        return out


    def _render_client(self, ir: IR_Spec, raw_spec: dict) -> str:
        class_name   = self._client_class_name(ir.title)
        timestamp    = datetime.datetime.utcnow().isoformat() + 'Z'
        sections     = []

        # file header
        sections.append(self._render_header(ir, timestamp))
        sections.append(self._render_imports())
        sections.append(self._render_config_and_http_classes())
        sections.append(self._render_client_class(class_name, ir))

        return "\n".join(sections)

    def _client_class_name(self, title: str) -> str:
        name = re.sub(r'[^a-zA-Z0-9]+', '_', title).strip('_')
        if not name:
            name = 'Service'
        return f"{self.class_name_prefix}{name}"

    # ---- code snippets ----

    def _render_header(self, ir: IR_Spec, timestamp: str) -> str:
        return f"""# Auto-generated client for {ir.title}
#   spec_version : {ir.version}
#   spec_hash    : {ir.spec_hash}
#   generated_at : {timestamp}
#   generator    : OpenAPI__To__Python"""

    def _render_imports(self) -> str:
        return """
import requests
import urllib.parse
from typing                                                              import Any, Dict, Optional
from osbot_utils.type_safe.Type_Safe                                     import Type_Safe
from osbot_utils.type_safe.primitives.core.Safe_Int                      import Safe_Int
from osbot_utils.type_safe.primitives.domains.web.safe_str.Safe_Str__Url import Safe_Str__Url

"""

    def _render_config_and_http_classes(self) -> str:
        return """
class Fast_API__Client__Config(Type_Safe):
    base_url        : Safe_Str__Url = None
    timeout_sec     : Safe_Int      = 30
    bearer_token    : str           = None
    api_key_name    : str           = None
    api_key_value   : str           = None
    headers         : Dict[str, str]

class Fast_API__Client__Http(Type_Safe):
    config: Fast_API__Client__Config

    def headers(self) -> Dict[str, str]:
        headers = self.config.headers.copy()
        if self.config.bearer_token:
            headers['Authorization'] = f'Bearer {self.config.bearer_token}'
        if self.config.api_key_name and self.config.api_key_value:
            headers[str(self.config.api_key_name)] = str(self.config.api_key_value)
        return headers

    def build_url(self, path: str, query: Dict[str, Any] = None) -> str:
        base = str(self.config.base_url).rstrip('/')
        path = '/' + path.lstrip('/')
        if query:
            q = {k: v for k, v in query.items() if v is not None}  # Drop None values
            if q:
                return base + path + '?' + urllib.parse.urlencode(q, doseq=True)
        return base + path

    def request_json(self, method: str                   ,  # HTTP method (GET, POST, etc.)
                           path  : str                   ,  # URL path
                           query : Dict[str, Any] = None ,  # Query parameters
                           body  : Any            = None    # Request body
                      ) -> Any   :                          # JSON object or string response
        url = self.build_url(path, query)
        headers = self.headers()

        response = requests.request(method  = method ,
                                    url     = url    ,
                                    headers = headers,
                                    json    = body if isinstance(body, (dict, list)) else None,
                                    data    = body if not isinstance(body, (dict, list)) else None,
                                    timeout=int(self.config.timeout_sec))
        response.raise_for_status()

        if response.headers.get('Content-Type', '').startswith('application/json'):
            return response.json()
        return response.text
"""

    def _render_client_class(self, class_name: str, ir: IR_Spec) -> str:
        methods_section = self._render_methods(ir)

        return f"""
class {class_name}(Type_Safe):
    config : Fast_API__Client__Config
    http   : Fast_API__Client__Http

    def __init__(self, url:Safe_Str__Url=None, **kwargs):
        super().__init__(**kwargs)
        if url:
            self.config.base_url = url
        self.http   = Fast_API__Client__Http(config=self.config)

{methods_section}"""

    def _render_methods(self, ir: IR_Spec) -> str:
        # Group by tag
        groups: Dict[str, List[IR_Operation]] = {}
        for op in ir.operations:
            tag = str(op.tag) if op.tag else 'default'
            groups.setdefault(tag, []).append(op)

        lines: List[str] = []
        for tag in sorted(groups.keys()):
            if self.prefer_tag_sections:
                lines.append(f"\n    # -------------------- tag: {tag} --------------------\n")
            for op in groups[tag]:
                lines.append(self._render_method(op))
        return "".join(lines)

    def _render_method(self, op: IR_Operation) -> str:
        # Build signature - keeping it simple for the ping example
        sig_parts = ["self"]
        sig_parts.append("timeout_sec: Optional[int] = None")
        sig = ", ".join(sig_parts)

        # Build path (for simple case without parameters)
        path_expr = f"f'{op.path}'"

        # Method docstring
        summary = str(op.summary) if op.summary else f"{op.method} {op.path}"
        doc = f'""" {summary} """'

        return f"""
    def {op.operation_id}({sig}):
        {doc}
        if timeout_sec is not None:
            self.config.timeout_sec = timeout_sec

        path   = {path_expr}
        query  = None
        return self.http.request_json(method='{op.method}', path=path, query=query)
"""
