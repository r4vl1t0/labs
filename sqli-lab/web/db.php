<?php

$conn = new mysqli(
    "mysql",
    "lab",
    "lab",
    "lab"
);

if($conn->connect_error){
    die("Connection failed");
}

?>
