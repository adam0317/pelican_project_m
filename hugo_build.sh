sitename=$1
staging_path=$2/wasabi/$sitename
build_path=$3

cd $build_path

# currentDate=`date +"%Y-%m-%d %T"`
# echo $currentDate
HUGO_UGLYURLS=true hugo --log --verboseLog=true

echo "Starting Hugo Move Files"
mkdir -p $staging_path
cp -f -r $build_path/public/* $staging_path

echo "Starting Zip Files"
mkdir -p $2/zip
cd $2/zip
zip -q -r $sitename.zip $build_path/public

# echo "Uploading Zip Files To Wasabi"
# aws s3 cp --profile wasabi $2/zip/$sitename.zip s3://hugo-project-m-zip-files/$sitename/ --endpoint-url=https://s3.us-west-1.wasabisys.com

echo "Uploading Zip Files To AWS"
aws s3 mv $2/zip/$sitename.zip s3://hugo-project-m-zip-files/$sitename/

echo "Deleting Build Files"
rm -rf $build_path
