### Is there an updates in submodule?
git submodule update --init

### publish dir
cd public
git checkout master
cd ..

### generate all files
hugo

### publish dir
cd public
git add .
git commit -m 'xxx'
git push origin master -f
cd ..

### source the last ---------------------
git add .
git commit -m "$1"
git push origin master -f


# picture url
# https://raw.githubusercontent.com/mobilephone724/blog_pictures/master
