<?php

if ($argv[1]) {
    $start = strtotime($argv[1]);
} else {
    $start = strtotime('2020-01-01');
    }
$end = time();
echo $start;
for ($i=0; $i < 10; $i++) { 
    $timestamp = mt_rand($start, $end);
    
    echo date('Y-m-d', $timestamp);
    echo "\n";
    # code...
}

// Declare two dates
$Date1 = '01-10-2010';
$Date2 = '05-10-2010';
  
// Declare an empty array
$array = array();
  
// Use strtotime function
$Variable1 = strtotime($Date1);
$Variable2 = strtotime($Date2);
  
// Use for loop to store dates into array
// 86400 sec = 24 hrs = 60*60*24 = 1 day
for ($currentDate = $Variable1; $currentDate <= $Variable2; 
                                $currentDate += (86400)) {
                                      
$Store = date('Y-m-d', $currentDate);
$array[] = $Store;
}
  
// Display the dates in array format
$rand_keys = array_rand($array);

$myfile = fopen("test.html", "w");

fwrite($myfile, "---\n");
fwrite($myfile, "title: \n");
fwrite($myfile, "cover:\n");
fwrite($myfile, "  image: {featured_image}\n");
fwrite($myfile, "  hidden: false\n");
fwrite($myfile, "  alt: \n");
fwrite($myfile, "date: ".$array[$rand_keys]."\n");
fwrite($myfile, "draft: false\n");
fwrite($myfile, "keywords: \n");
fwrite($myfile, "---\n\n");



fclose($myfile);