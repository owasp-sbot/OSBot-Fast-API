git pull
git checkout main
git pull origin main
git merge --no-ff dev -m "Merge dev into main"
git push origin main
git checkout dev
git merge main -m "Merge main into dev"