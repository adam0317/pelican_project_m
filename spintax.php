<?php
// require 'vendor/autoload.php';

// use League\HTMLToMarkdown\HtmlConverter;

// $converter = new HtmlConverter();

$csvFilePath = $argv[1];
$articleDir = $argv[2];
$articleDst = $argv[3];
if ($argv[4]) {
    $start_date = strtotime($argv[4]);
} else {
    $start_date = strtotime('2020-01-01');
}

$end_date = time();

class Spintax
{
    static $countBlocks = 0;
    static $blocks = [];

    public static function Parse($text, $count = [])
    {
        if (strpos($text, '#block#') !== false) {
            $text = preg_replace_callback('|#block#(.*?)#/block#|si', ['Spintax', 'replaceBlock'], $text);

            $newBlocks = self::$blocks;
            shuffle($newBlocks);

            $count_from = $count_to = 0;
            if (!empty($count)) {
                $count_from = (int) $count[0] > 0 ? (int) $count[0] : 1;
                $count_to = ((int) $count[1] == 0 || (int) $count[1] > count($newBlocks)) ? count($newBlocks) : (int) $count[1];
            }

            $cntBlocks = rand($count_from, $count_to);
            $cntBlocks = ($cntBlocks == 0 || $cntBlocks > count($newBlocks)) ? count($newBlocks) : $cntBlocks;

            for ($i = 0; $i < $cntBlocks; $i++) {
                $p = implode("\n", $newBlocks[$i]);
                $text = str_replace('{#block' . ($i + 1) . '#}', $p, $text);
            }

            $text = preg_replace('|{#block.*?#}|si', '', $text);

            self::$countBlocks = 0;
            self::$blocks = array();
        }

        return self::Process($text);
    }

    private static function replaceBlock($text)
    {
        if (!empty($text[1])) {
            preg_match_all('|#p#(.*?)#/p#|si', $text[1], $matches);
            if (!empty($matches[1])) {
                $p = $matches[1];
                shuffle($p);

                foreach ($p as $key => $val) {
                    if (empty($val)) continue;

                    $test = explode('#s#', $val);
                    $index = array_rand($test, 1);
                    $test = $test[$index];

                    $test = explode("\n", $test);
                    shuffle($test);

                    $text = implode("\n", $test);

                    self::$blocks[self::$countBlocks][] = $text;
                }
            } else {
                self::$blocks[self::$countBlocks][] = trim($text[1]);
            }
        }

        self::$countBlocks++;
        return '{#block' . self::$countBlocks . '#}';
    }

    private static function Process($text)
    {
        $pattern = '/\{(((?>[^\{\}]+)|(?R))*)\}/x';
        return preg_replace_callback($pattern, ['Spintax', 'Replace'], $text);
    }

    private static function Replace($text)
    {
        $text = self::Process($text[1]);
        $parts = explode('|', $text);

        return $parts[array_rand($parts)];
    }
}

// Create destination
if (!is_dir($articleDst)) {
    mkdir($articleDst, 0777, true);
}

// Read content file
$input = array_diff(scandir($articleDir), array('..', '.'));;
$start_time = microtime(true);

// Read CSV file
$file = fopen($csvFilePath, "r");
while (!feof($file)) {
    $timestamp = mt_rand($start_date, $end_date);

    $post_date =  date('Y-m-d', $timestamp);
    $rand_keys = array_rand($input);

    $text = file_get_contents($articleDir . '/' . $input[$rand_keys]);
    $keyword = fgetcsv($file)[0];
    $myfile = fopen("$articleDst/$keyword.md", "w") or die("Unable to open file!");
    $spun_doc = Spintax::parse($text);
    // $doc = new DOMDocument();
    // @$doc->loadHTML($text);

    // $tags = $doc->getElementsByTagName('img');
    // foreach ($tags as $tag) {
    //     echo $tag->getAttribute('src');
    // }
    fwrite($myfile, "---\n");
    fwrite($myfile, "title: " . $keyword . "\n");
    // fwrite($myfile, "cover:\n");
    // fwrite($myfile, "  image: {featured_image}\n");
    // fwrite($myfile, "  hidden: false\n");
    // fwrite($myfile, "  alt: \n");
    fwrite($myfile, "date: " . $post_date . "\n");
    fwrite($myfile, "draft: false\n");
    fwrite($myfile, "keywords: ['" . $keyword . "']\n");
    fwrite($myfile, "---\n\n");
    // $mydoc = $converter->convert($spun_doc);
    fwrite($myfile, $spun_doc);
    fclose($myfile);
}
fclose($file);

$end_time = microtime(true);
$execution_time = ($end_time - $start_time);


echo " Execution time of script = " . $execution_time . " sec\n";
