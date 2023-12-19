<?php
  require_once('./private/db.php');

  try {
    $mongo = new MongoDB\Driver\Manager("mongodb://localhost:27017");
  } catch (MongoDB\Driver\Exception\InvalidArgumentException $me) {
    print ('MongoDB Driver Error ') . $me->getMessage();
    die;
  } catch (MongoDB\Driver\Exception\RuntimeException $re) {
    print ('MongoDB uri Error ') . $re->getMessage();
    die;
  }
  $people=[];
  // Arrays
  // birthPlace
  $peopleBirthPlace=[];
  // deathPlace
  $peopleDeathPlace=[];
  // birthYear
  $peopleBirthYear=[];
  // deathYear
  $peopleDeathYear=[];
  // chaptersWritten
  $peopleChaptersWritten=[];
  // children
  $peopleChildren=[];
  // eastons
  $peopleEastons=[];
  // eventGroups
  $peopleEventGroups=[];
  // events
  $peopleEvents=[];
  // father
  $peopleFather=[];
  // mother
  $peopleMother=[];
  // siblings
  $peopleSiblings=[];
  // halfSiblingsSameFather
  $peopleHalfSiblingsSameFather=[];
  // halfSiblingsSameMother
  $peopleHalfSiblingsSameMother=[];
  // memberOf
  $peopleMemberOf=[];
  // partners
  $peoplePartners=[];
  // timeline
  $peopleTimeline=[];
  // verses
  $peopleVerses=[];

  // Scholor
  // alphaGroup:String
  // alsoCalled:String
  // ambiguous:boolean
  // Disambiguation (temp):string
  // displayTitle:string
  // Easton's Count:int
  // gender:string
  // isProperName:boolean
  // maxYear:int
  // minYear:int
  // name:string
  // verseCount:int
  // surname:string

  // No filter
  $filter = [];
  // fields(Projectopn)
  $options = [
    'projection' => array(
      "_id" => 0
    )//,
    //'sort' => array("Sort Key 1" => 1, "Sort Key 2" => 1)
  ];
  // Query
  $query = new MongoDB\Driver\Query($filter, $options);
  $cursor = $mongo->executeQuery('theographic_bible_metadata.peopleGroups', $query);
  $cursor->setTypeMap(['root' => 'array', 'document' => 'array', 'array' => 'array']);
  foreach ($cursor as $document) {
    $id = $document["id"];
    $fields = $document["fields"];
      if (array_key_exists("alphaGroup", $fields)) {
        $people[$id]["alphaGroup"]=$fields["alphaGroup"];
      } else {
        $people[$id]["alphaGroup"]=NULL;
      }
      if (array_key_exists("alsoCalled", $fields)) {
        $people[$id]["alsoCalled"]=$fields["alsoCalled"];
      } else {
        $people[$id]["alsoCalled"]=NULL;
      }

      $has_Events = TRUE;
      if (array_key_exists("events", $fields)) {
        $has_Events = TRUE;
      } else {
        $has_Events = FALSE;
      }

      $has_EventsDev = TRUE;
      if (array_key_exists("events_dev", $fields)) {
        $has_EventsDev = TRUE;
      } else {
        $has_EventsDev = FALSE;
      }

      $has_Members = TRUE;
      if (array_key_exists("members", $fields)) {
        $has_Members = TRUE;
      } else {
        $has_Members = FALSE;
      }

      $has_PartOf = TRUE;
      if (array_key_exists("partOf", $fields)) {
        $has_PartOf = TRUE;
      } else {
        $has_PartOf = FALSE;
      }
      $sth->bindValue('has_PartOf', $has_PartOf, PDO::PARAM_BOOL);

      $has_Verses = TRUE;
      if (array_key_exists("verses", $fields)) {
        $has_Verses = TRUE;
      } else {
        $has_Verses = FALSE;
      }
    }
  /**
   * peopleBase Structure
   * | id               | varchar(32) | NO   | PRI | NULL    |       |
   * | yearNum          | int(11)     | NO   |     | NULL    |       |
   * | isoYear          | int(11)     | NO   |     | NULL    |       |
   * | BC_AD            | varchar(8)  | YES  |     | NULL    |       |
   * | formattedYear    | varchar(16) | NO   |     | NULL    |       |
   * | has_booksWritten | tinyint(1)  | NO   |     | 0       |       |
   * | has_ebookId      | tinyint(1)  | NO   |     | 0       |       |
   * | has_peopleBorn   | tinyint(1)  | NO   |     | 0       |       || has_peopleDied   | tinyint(1)  | NO   |     | 0       |       |
   */
  // Local Maria DB ready
  /*
  try {
    $pdo = new PDO("mysql:host=localhost;dbname=theo", $user, $pw);
    $sql = 'INSERT INTO peopleGroupsBase(id, groupName, has_Events, has_EventsDev, has_Members, has_PartOf, has_Verses) VALUES (:id, :groupName, :has_Events, :has_EventsDev, :has_Members, :has_PartOf, :has_Verses);';
    $sth = $pdo->prepare($sql, [PDO::ATTR_CURSOR => PDO::CURSOR_FWDONLY]);

    $pdo->beginTransaction();
    foreach ($cursor as $document) {
      $id = $document["id"];
      $sth->bindValue('id', $id, PDO::PARAM_STR);
      $fields = $document["fields"];
      $groupName = NULL;
      if (array_key_exists("groupName", $fields)) {
        $groupName = $fields["groupName"];
        $sth->bindValue('groupName', $groupName, PDO::PARAM_STR);
      } else {
        $groupName = NULL;
        $sth->bindValue('groupName', $groupName, PDO::PARAM_NULL);
      }

      $has_Events = TRUE;
      if (array_key_exists("events", $fields)) {
        $has_Events = TRUE;
      } else {
        $has_Events = FALSE;
      }
      $sth->bindValue('has_Events', $has_Events, PDO::PARAM_BOOL);

      $has_EventsDev = TRUE;
      if (array_key_exists("events_dev", $fields)) {
        $has_EventsDev = TRUE;
      } else {
        $has_EventsDev = FALSE;
      }
      $sth->bindValue('has_EventsDev', $has_EventsDev, PDO::PARAM_BOOL);

      $has_Members = TRUE;
      if (array_key_exists("members", $fields)) {
        $has_Members = TRUE;
      } else {
        $has_Members = FALSE;
      }
      $sth->bindValue('has_Members', $has_Members, PDO::PARAM_BOOL);

      $has_PartOf = TRUE;
      if (array_key_exists("partOf", $fields)) {
        $has_PartOf = TRUE;
      } else {
        $has_PartOf = FALSE;
      }
      $sth->bindValue('has_PartOf', $has_PartOf, PDO::PARAM_BOOL);

      $has_Verses = TRUE;
      if (array_key_exists("verses", $fields)) {
        $has_Verses = TRUE;
      } else {
        $has_Verses = FALSE;
      }
      $sth->bindValue('has_Verses', $has_Verses, PDO::PARAM_BOOL);

      $sth->execute();
      //$sth->debugDumpParams();
    }
    $pdo->commit();
    echo "commiter<br>";
  } catch (PDOException $e) {
    print $e->getMessage();
    echo "<br><hr>";
    print $e->getTraceAsString();
    echo "<br><hr>";
    $pdo->rollBack();
  }
  $sth = null;
  $pdo = null;
  */
?>