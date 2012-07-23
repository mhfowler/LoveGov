LG="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $LG
git checkout dev
git add -i
git commit -a -m "merge."
git push origin dev
git checkout master
git merge dev
git pull origin master
git commit -a -m "merge."
git push origin master
git checkout dev
cd -
