# Data Warehouse Project

### Table of contents
> [Introduction](#Introduction)<br>
  [I. Project Description](#Projectdescription)<br>
  [II. Sparkify Data Warehouse Architecture](#named)<br>
  [III. Project Implementation](#implementation)<br>
  [IV. Execution](#Execution)<br>

### Introduction
This project consist to build a data warehouse based on AWS for a music streaming startup Sparkify.
As sparkify's users base and songs database keep to grow, they want to have a new system to adapt that evoluation of data.

### I. Project description
To build that data warehouse, we have to use sparky log data that store in different JSON files and these log files are store onto AWS s3 bucket.
In first time we will create an AWS redshift cluster and design different tables that fit with different log files and modeling sparky analytic system with a star schema to help the analysis team to do easily their works. 
After designed tables, we create an ETL pipeline to load the data from the log files that store in S3 bucket and populate the different tables.

### II. Sparkify Data Warehouse Architecture

#### 1. Data source
In this project we are working with two datasets that store into diferent S3 directory named  ==*s3://udacity-dend/song_data*== and ==*s3://udacity-dend/log_data*== . Each dataset contains several JSON files. 
* **song_data** contains metadata about a song and the artist of that song. In below a sample of data json file
![Imgur](https://i.imgur.com/zi9933K.png)


* **log_data** contains the log events based on the songs in the dataset song_data. In below a sample of data json file
  ![Imgur](https://i.imgur.com/tVeYup8.png)

#### 2. Redshift Cluster
As host server to store sparkify database, we created a redshift cluster that has the follow caracteristics:

##### a. Cluster details:
* *Type of nodes:* **dc2.large**
* *Number of nodes:* **2**
* *Storage:* **320 Go**

##### b. Database informations
* *DB name:* **sparkify**
* *Port:* **5439**
* *Cluster Identifier:* **awsuser**

##### c. IAM Roles
We created an IAM role and attached AmazonS3ReadOnlyAccess policy befor applyed it on our cluster. 

### 3. Data warehouse's database 
To build our data warehouse, we decided to shape the database in two differents structures. One structure will be use to load data from the different datasets and another structure that modeling sparkify analytics team activities.

##### a. Data Loading tables 
As we have two different dataset, we created two tables:  to load log data. Each table will load all JSON contains into each dataset. 

##### b. Analytics data structure
Here we designed a star schema to create fact and dimension tables. we are four dim tables (**artists, users, songs, times**) and a fact table **songplay**. 
The data we load into these table provide from two tables we created to load the log data. 
To optimize the processes on these tables, we designed all dimension tables with **distribution style all** and put a **sortkey** on one column of each tables.
As the fact table add a new row whenever an event happen in the streaming music, it can be grow faster and became a very big table. So to optimize the processes on that table, we used **sortkey** and **distkey** style distribution.

##### c. Tables structures

-[x] **staging_events:**  load data from log_data dataset
> events_key   INTEGER IDENTITY(0,1) NOT NULL,
   artist        VARCHAR,
   auth          VARCHAR    NOT NULL,
   firstName     VARCHAR,
   gender        VARCHAR(1),
   itemInSession INTEGER,
   lastName      VARCHAR,
   lenght        DECIMAL,
   level         VARCHAR(4) NOT NULL,
   location      VARCHAR,
   method        VARCHAR(4) NOT NULL,
   page          VARCHAR    NOT NULL,
   registration  VARCHAR,
   sessionId     INTEGER,
   song          VARCHAR,
   status        INTEGER,
   ts            BIGINT     NOT NULL,
   userAgent     VARCHAR,
   userId        INTEGER 
   
-[x] **staging_songs:** load data from song_data dataset
> num_songs        INTEGER NOT NULL,
  artist_id        VARCHAR NOT NULL,
  artist_latitude  VARCHAR,
  artist_longitude VARCHAR,
  artist_location  VARCHAR,
  artist_name      VARCHAR,
  song_id          VARCHAR NOT NULL,
  title            VARCHAR NOT NULL,
  duration         DECIMAL NOT NULL,
  year             INTEGER NOT NULL

-[x] **songplay:** Fact Table
>   songplay_id   INTEGER IDENTITY(0,1) PRIMARY KEY NOT NULL,
    start_time    TIMESTAMP  NOT NULL sortkey,
    user_id       INTEGER,
    level         VARCHAR(4) NOT NULL,
    song_id       VARCHAR    NOT NULL distkey,
    artist_id     VARCHAR    NOT NULL,
    session_id    INTEGER,
    location      VARCHAR,
    user_agent    VARCHAR
 
-[x] **users:** Dim table
>(user_key   INTEGER IDENTITY(0,1) NOT NULL PRIMARY KEY,
 user_id    INTEGER  sortkey,
 first_name VARCHAR,
 last_name  VARCHAR,
 gender     VARCHAR(1),
 level      VARCHAR(4) NOT NULL
)diststyle all

-[x] **songs:** Dim table
>(song_id    VARCHAR NOT NULL PRIMARY KEY sortkey,
     title      VARCHAR NOT NULL,
     artist_id  VARCHAR NOT NULL,
     year       INTEGER NOT NULL,
     duration   DECIMAL NOT NULL
     )diststyle all
 
-[x] **artists:** Dim table
>artist_id VARCHAR NOT NULL PRIMARY KEY sortkey,
 name      VARCHAR,
 location  VARCHAR,
 lattitude VARCHAR,
 longitude VARCHAR
 )diststyle all
 
 -[x] **times:** Dim table 
> (ts       BIGINT NOT NULL PRIMARY KEY sortkey,
 start_time TIMESTAMP NOT NULL,
 hour       INTEGER NOT NULL,
 day        INTEGER NOT NULL,
 week       INTEGER NOT NULL,
 month      INTEGER NOT NULL,
 year       INTEGER NOT NULL,
 weekday    INTEGER NOT NULL
)diststyle all

### III. Project implementation

### 1. Scripts
To realize sparkify's data warehouse, we implemented our code in four steps: 
* *Step 1 (SQL Script) :* In this step, we writed SQL statement into python file to drop tables if exists before create each tables of our systeme.
* *Step 2 (Execution of SQL statement):* After created different SQL statement, we writed another code to connect to the database and execute SQL statement to create these tables.
* *Step 3 (ETL Script): We create another python code to connect to redsift cluster and load data from S3 bucket to staging tables that we created.

*Note: We created also a conf file to define datasets path and cluster parameters to them into different scripts.*  

### 2. Files
This project contains these five follow files:
* *sql_queries.py:* file that contains SQL Statement to create and drop tables
* *create_tables.py* file that we run to connect and create tables to the redshift cluster
* *etl.py* file that implement the logic to extract data from the S3 bucket and load to tables. We also need to connect to the cluster.
* *dwh.cfg:* This file contains the cluster parameters and different dataset path 
* *Reamde.md* This is a currutly file in which we describe the project.

Example of codes
* SQL statement
 

### IV. Execution

#### 1. Script runnig Screenshot 
![Executyion](https://i.imgur.com/c26SSl3.png?1)

#### 2. Tables Screenshot

##### a. Songplay table
![Imgur](https://i.imgur.com/TQpzVYh.png)

##### b. staging_song table
![Imgur](https://i.imgur.com/URAV2ge.png)
