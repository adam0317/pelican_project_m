sitename=$1
staging_path=$2/wasabi/$sitename
build_path=$3

cd $build_path

HUGO_UGLYURLS=true hugo 

echo "Starting Hugo Move Files"
mkdir -p $staging_path
cp -f -r $build_path/public/* $staging_path

echo "Starting Zip Files"
mkdir -p $2/zip
cd $2/zip
zip -r $sitename.zip $build_path/public

echo "Deleting Build Files"
rm -rf $build_path
