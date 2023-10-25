<!DOCTYPE html>
<html lang="ja">

<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Document</title>
</head>

<body>
  <?php
  $cnt = 0;
  $treeLuke = [];
  $lineByLuke = ['Adam', 'Seth', 'Enosh', 'Kenan', 'Mahalalel', 'Jared', 'Enoch', 'Methuselah', 'Lamech', 'Noah', 'Shem', 'Arphaxad', 'Cainan', 'Shelah', 'Eber', 'Peleg', 'Reu', 'Serug', 'Nahor', 'Terah', 'Abraham', 'Isaac', 'Jacob', 'Judah', 'Perez', 'Hezron', 'Ram', 'Amminadab', 'Nahshon', 'Salmon', 'Boaz', 'Obed', 'Jesse', 'David', 'Nathan', 'Mattatha', 'Menna', 'Melea', 'Eliakim', 'Jonam', 'Joseph', 'Judah', 'Simeon', 'Levi', 'Matthat', 'Jorim', 'Eliezer', 'Joshua', 'Er', 'Elmadam', 'Cosam', 'Addi', 'Melki', 'Neri', 'Shealtiel', 'Zerubbabel', 'Rhesa', 'Joanan', 'Joda', 'Josek', 'Semein', 'Mattathias', 'Maath', 'Naggai', 'Esli', 'Nahum', 'Amos', 'Mattathias', 'Joseph', 'Jannai', 'Melki', 'Levi', 'Matthat', 'Heli', 'Joseph', 'Jesus'];
  $lineByMatthew = ['Abraham', 'Isaac', 'Jacob', 'Judah', 'Perez', 'Hezron', 'Ram', 'Amminadab', 'Nahshon', 'Salmon', 'Boaz', 'Obed', 'Jesse', 'David', 'Solomon', 'Rehoboam', 'Abijah', 'Asa', 'Jehoshaphat', 'Jehoram', 'Uzziah', 'Jotham', 'Ahaz', 'Hezekiah', 'Manasseh', 'Amon', 'Josiah', 'Jeconiah ', 'Shealtiel', 'Zerubbabe', 'Abihud', 'Eliakim', 'Azor', 'Zadok', 'Akim', 'Elihud', 'Eleazar', 'Matthan', 'Jacob', 'Joseph', 'Jesus'];
  try {
    $mongo = new MongoDB\Driver\Manager("mongodb://localhost:27017");
  } catch (MongoDB\Driver\Exception\InvalidArgumentException $me) {
    print ('MongoDB Driver Error ') . $me->getMessage();
    die;
  } catch (MongoDB\Driver\Exception\RuntimeException $re) {
    print ('MongoDB uri Error ') . $re->getMessage();
    die;
  }
  // Luke's line
  $filter = ["fields.name" => $lineByLuke[$cnt]];
  // fields(Projectopn)
  $options = [
    'projection' => array(
      "_id" => 0,
      "fields.personLookup" => 0,
      "fields.personID" => 0,
      "fields.memberOf" => 0,
      "fields.birthYear" => 0,
      "fields.deathYear" => 0,
      "fields.birthPlace" => 0,
      "fields.events" => 0,
      "fields.slug" => 0,
      "fields.eventGroups" => 0,
      "fields.dictionaryText" => 0,
      "fields.verses" => 0,
      "fields.status" => 0,
      "fields.eastons" => 0,
      "fields.timeline" => 0,
      "fields.verseCount" => 0,
      "fields.alphaGroup" => 0,
      "fields.Easton's Count" => 0,
      "fields.dictText" => 0,
      "fields.modified" => 0,
      "createdTime" => 0
    )
  ];
  // Query
  $query = new MongoDB\Driver\Query($filter, $options);
  $cursor = $mongo->executeQuery('theographic_bible_metadata.people', $query);
  $cursor->setTypeMap(['root' => 'array', 'document' => 'array', 'array' => 'array']);
  foreach ($cursor as $document) {
    $id;
    foreach ($document as $item) {
      $name = NULL;
      if(is_array($item)) {
        foreach($item as $key => $value) {
          if(is_array($value)) {
            for($i=0; $i < count($value); $i++) {

              echo 'Array ' . $key . ' : ' . $value[$i] . nl2br('<br>');
            }
          } else {
            /**
             * TODO:
             * Get Person's name first to determine the root key.
             */
            if(strcmp($key, 'name')) {
              if(strcmp($value, $lineByLuke[$cnt])) {
                $treeLuke[$value]['id'] = $id;
                $name = $value;
              }
            }
            if(strcmp($key, 'alsoCalled')) {
              if(!$name && strcmp($value, $lineByLuke[$cnt])) {
                $treeLuke[$value]['id'] = $id;
                $name = $value;
              }
            }
            echo 'Not Array ' . $key . ' : ' . $value . nl2br('<br>');
          }
        }
      } else {
        $id = $item;
        echo $id . nl2br('<br>');
      }
    }
  }
  ?>
</body>

</html>