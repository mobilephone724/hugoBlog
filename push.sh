# submodule first
hugo
cd public
git add .
git commit -m "$1"
git push origin master

# then source
cd ..
git add .
git commit -m "$1"
git push origin master