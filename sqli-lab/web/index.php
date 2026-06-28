<?php

include 'db.php';

$result = "";

if(isset($_GET['id'])){

    $id = $_GET['id'];

    $query = "SELECT * FROM users WHERE id = '$id'";

    $sql = $conn->query($query);

    while($row = $sql->fetch_assoc()){
        $result .= $row['username']."<br>";
    }
}

?>

<form>

<input name="id">

<input type="submit">

</form>

<hr>

<?php

echo $result;

?>
