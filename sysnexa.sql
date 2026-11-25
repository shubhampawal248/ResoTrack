-- MySQL dump 10.13  Distrib 8.0.46, for Win64 (x86_64)
--
-- Host: localhost    Database: sysnexa
-- ------------------------------------------------------
-- Server version	8.0.46

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `sysnexa`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `sysnexa` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `sysnexa`;

--
-- Table structure for table `execution_history`
--

DROP TABLE IF EXISTS `execution_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `execution_history` (
  `execution_id` int NOT NULL AUTO_INCREMENT,
  `task_id` varchar(100) NOT NULL,
  `pid` int DEFAULT NULL,
  `execution_time_seconds` decimal(10,3) DEFAULT NULL,
  `cpu_time_seconds` decimal(10,3) DEFAULT NULL,
  `cpu_percent` decimal(5,2) DEFAULT NULL,
  `peak_memory_mb` decimal(12,2) DEFAULT NULL,
  `exit_code` int DEFAULT NULL,
  `result_status` varchar(30) DEFAULT NULL,
  `executed_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`execution_id`),
  KEY `task_id` (`task_id`),
  CONSTRAINT `execution_history_ibfk_1` FOREIGN KEY (`task_id`) REFERENCES `workloads` (`task_id`)
) ENGINE=InnoDB AUTO_INCREMENT=33 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `execution_history`
--

LOCK TABLES `execution_history` WRITE;
/*!40000 ALTER TABLE `execution_history` DISABLE KEYS */;
INSERT INTO `execution_history` VALUES (1,'TASK-20261123005417337555',426,10.716,5.016,99.57,9.38,0,'COMPLETED','2026-11-22 19:26:29'),(2,'TASK-20261123005511866523',438,1.291,0.019,1.89,9.25,0,'COMPLETED','2026-11-22 19:26:31'),(3,'TASK-20261123005602604277',445,2.285,0.025,1.22,9.13,0,'COMPLETED','2026-11-22 19:26:33'),(4,'SIM-20261124003840-13b1282e',473,11.611,2.065,50.58,12.63,0,'COMPLETED','2026-11-23 19:08:57'),(5,'SIM-20261124003840-1fba4af1',507,4.333,0.056,1.37,16.50,0,'COMPLETED','2026-11-23 19:09:01'),(6,'SIM-20261124003840-687709f5',541,4.342,0.076,1.86,12.78,0,'COMPLETED','2026-11-23 19:09:06'),(7,'SIM-20261124004816-ad0aec26',443,16.228,2.508,30.84,28.63,0,'COMPLETED','2026-11-23 19:18:36'),(8,'SIM-20261124004816-da290819',495,8.417,2.505,30.80,28.63,0,'COMPLETED','2026-11-23 19:18:45'),(9,'SIM-20261124004816-60c9a206',546,8.441,2.486,30.61,28.75,0,'COMPLETED','2026-11-23 19:18:53'),(10,'SIM-20261124010930-c01ca372',448,11.301,0.979,31.55,16.63,0,'COMPLETED','2026-11-23 19:40:07'),(11,'SIM-20261124010930-af38ecfa',472,3.384,0.969,31.29,16.63,0,'COMPLETED','2026-11-23 19:40:10'),(12,'SIM-20261124010930-39050400',497,3.331,0.960,31.06,16.63,0,'COMPLETED','2026-11-23 19:40:14'),(13,'SIM-20261124011334-9c62fa09',448,10.858,1.566,50.29,12.50,0,'COMPLETED','2026-11-23 19:43:47'),(14,'SIM-20261124011334-1a981d08',472,3.383,1.560,50.28,12.50,0,'COMPLETED','2026-11-23 19:43:51'),(15,'SIM-20261124011334-f719f2ad',497,3.367,1.548,50.15,12.50,0,'COMPLETED','2026-11-23 19:43:54'),(16,'SIM-20261124011525-8b0af6d6',441,11.118,1.579,50.52,12.50,0,'COMPLETED','2026-11-23 19:45:39'),(17,'SIM-20261124011525-2c3e1b0f',465,3.414,0.977,31.43,16.75,0,'COMPLETED','2026-11-23 19:45:43'),(18,'SIM-20261124011525-47ac681f',490,3.301,0.052,1.68,16.50,0,'COMPLETED','2026-11-23 19:45:46'),(19,'SIM-20261124012536-a54fa7ca',631,3.406,1.569,50.40,12.38,0,'COMPLETED','2026-11-23 19:56:06'),(20,'SIM-20261124012536-2263e124',761,3.347,1.551,49.91,12.50,0,'COMPLETED','2026-11-23 19:56:39'),(21,'SIM-20261124012536-b642557f',788,3.336,1.546,49.82,12.50,0,'COMPLETED','2026-11-23 19:56:42'),(22,'SIM-20261124234801-df3d0a4d',444,3.348,1.546,50.12,12.50,0,'COMPLETED','2026-11-24 18:19:07'),(23,'SIM-20261124234801-491ce16f',468,3.326,1.553,50.27,12.38,0,'COMPLETED','2026-11-24 18:19:10'),(24,'SIM-20261124234801-7bcb5152',493,3.325,1.548,50.11,12.50,0,'COMPLETED','2026-11-24 18:19:13'),(25,'TASK-20261125010713095409',421,4.209,0.032,57.14,11.63,0,'COMPLETED','2026-11-24 19:38:53'),(26,'SIM-20261125025904-4eb4e7ca',NULL,NULL,NULL,NULL,NULL,NULL,'FAILED','2026-11-24 21:29:11'),(27,'SIM-20261125025904-12e09c52',NULL,NULL,NULL,NULL,NULL,NULL,'FAILED','2026-11-24 21:29:15'),(28,'SIM-20261125025904-e0bfd0ab',NULL,NULL,NULL,NULL,NULL,NULL,'FAILED','2026-11-24 21:29:18'),(29,'SIM-20261125101910-26ee58ed',457,3.099,1.570,50.67,13.88,0,'COMPLETED','2026-11-25 04:49:22'),(30,'SIM-20261125101910-ad282541',456,3.098,1.568,50.62,13.88,0,'COMPLETED','2026-11-25 04:49:22'),(31,'SIM-20261125101910-c8673b59',458,3.097,1.568,50.63,14.00,0,'COMPLETED','2026-11-25 04:49:22'),(32,'TASK-20261125114218577734',423,0.042,0.041,98.18,14.00,0,'COMPLETED','2026-11-25 06:12:30');
/*!40000 ALTER TABLE `execution_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `load_runtime_readings`
--

DROP TABLE IF EXISTS `load_runtime_readings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `load_runtime_readings` (
  `reading_id` bigint NOT NULL AUTO_INCREMENT,
  `run_id` int NOT NULL,
  `cpu_percent` decimal(5,2) DEFAULT NULL,
  `memory_percent` decimal(5,2) DEFAULT NULL,
  `memory_used` bigint DEFAULT NULL,
  `memory_available` bigint DEFAULT NULL,
  `disk_percent` decimal(5,2) DEFAULT NULL,
  `disk_used` bigint DEFAULT NULL,
  `disk_free` bigint DEFAULT NULL,
  `recorded_at` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`reading_id`),
  KEY `run_id` (`run_id`),
  CONSTRAINT `load_runtime_readings_ibfk_1` FOREIGN KEY (`run_id`) REFERENCES `load_runtime_runs` (`run_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `load_runtime_readings`
--

LOCK TABLES `load_runtime_readings` WRITE;
/*!40000 ALTER TABLE `load_runtime_readings` DISABLE KEYS */;
INSERT INTO `load_runtime_readings` VALUES (1,1,2.33,12.47,492081152,3453927424,5.43,58717515776,1022383661056,'2026-11-23 00:53:30'),(2,1,1.83,12.35,487387136,3458621440,5.43,58717515776,1022383661056,'2026-11-23 00:53:34'),(3,1,1.67,12.46,491569152,3454439424,5.43,58717507584,1022383669248,'2026-11-23 00:53:38'),(4,1,1.67,12.44,491028480,3454980096,5.43,58717507584,1022383669248,'2026-11-23 00:53:41'),(5,1,1.83,12.48,492658688,3453349888,5.43,58717511680,1022383665152,'2026-11-23 00:53:45'),(6,1,1.83,12.04,475013120,3470995456,5.43,58717511680,1022383665152,'2026-11-23 00:53:49'),(7,1,1.67,12.01,473853952,3472154624,5.43,58717511680,1022383665152,'2026-11-23 00:53:52'),(8,1,1.83,12.03,474517504,3471491072,5.43,58717511680,1022383665152,'2026-11-23 00:53:56'),(9,1,1.67,11.96,471916544,3474092032,5.43,58717503488,1022383673344,'2026-11-23 00:54:00'),(10,1,0.00,11.69,461393920,3484614656,5.43,58717503488,1022383673344,'2026-11-23 00:54:03'),(11,2,2.50,12.66,499503104,3446505472,5.43,58718031872,1022383144960,'2026-11-23 01:32:08'),(12,3,2.34,12.64,498659328,3447349248,5.43,58718035968,1022383140864,'2026-11-23 01:32:45'),(13,4,2.16,12.05,475533312,3470475264,5.43,58718027776,1022383149056,'2026-11-23 01:32:56'),(14,4,1.66,12.11,478048256,3467960320,5.43,58718031872,1022383144960,'2026-11-23 01:32:59'),(15,4,1.67,12.11,477773824,3468234752,5.43,58718031872,1022383144960,'2026-11-23 01:33:03'),(16,4,1.67,12.08,476827648,3469180928,5.43,58718031872,1022383144960,'2026-11-23 01:33:07'),(17,4,1.83,12.09,477052928,3468955648,5.43,58718031872,1022383144960,'2026-11-23 01:33:10'),(18,4,0.67,11.76,464105472,3481903104,5.43,58718023680,1022383153152,'2026-11-23 01:33:14'),(19,5,2.00,11.98,472555520,3473453056,5.43,58718023680,1022383153152,'2026-11-23 01:33:26'),(20,5,1.66,12.03,474509312,3471499264,5.43,58718023680,1022383153152,'2026-11-23 01:33:29'),(21,5,1.67,12.03,474853376,3471155200,5.43,58718023680,1022383153152,'2026-11-23 01:33:33');
/*!40000 ALTER TABLE `load_runtime_readings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `load_runtime_runs`
--

DROP TABLE IF EXISTS `load_runtime_runs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `load_runtime_runs` (
  `run_id` int NOT NULL AUTO_INCREMENT,
  `test_name` varchar(150) NOT NULL,
  `scenario_name` varchar(100) NOT NULL,
  `start_time` datetime NOT NULL,
  `end_time` datetime DEFAULT NULL,
  `duration_seconds` int DEFAULT NULL,
  `average_cpu` decimal(5,2) DEFAULT NULL,
  `peak_cpu` decimal(5,2) DEFAULT NULL,
  `average_memory` decimal(5,2) DEFAULT NULL,
  `peak_memory` decimal(5,2) DEFAULT NULL,
  `average_disk` decimal(5,2) DEFAULT NULL,
  `peak_disk` decimal(5,2) DEFAULT NULL,
  `status` varchar(30) DEFAULT 'RUNNING',
  PRIMARY KEY (`run_id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `load_runtime_runs`
--

LOCK TABLES `load_runtime_runs` WRITE;
/*!40000 ALTER TABLE `load_runtime_runs` DISABLE KEYS */;
INSERT INTO `load_runtime_runs` VALUES (1,'SysNexa_Test_20261123_004903','CPU Load','2026-11-23 00:53:23','2026-11-23 00:54:03',40,1.63,2.33,12.19,12.48,5.43,5.43,'COMPLETED'),(2,'SysNexa_Test_20261123_005900','CPU Load','2026-11-23 01:32:01','2026-11-23 01:32:09',8,2.50,2.50,12.66,12.66,5.43,5.43,'STOPPED'),(3,'SysNexa_Test_20261123_013228','CPU Load','2026-11-23 01:32:41','2026-11-23 01:32:47',6,2.34,2.34,12.64,12.64,5.43,5.43,'STOPPED'),(4,'SysNexa_Test_20261123_013228','CPU Load','2026-11-23 01:32:55','2026-11-23 01:33:14',19,1.61,2.16,12.03,12.11,5.43,5.43,'STOPPED'),(5,'SysNexa_Test_20261123_013228','CPU Load','2026-11-23 01:33:25','2026-11-23 01:33:35',10,1.78,2.00,12.01,12.03,5.43,5.43,'STOPPED');
/*!40000 ALTER TABLE `load_runtime_runs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `query_history`
--

DROP TABLE IF EXISTS `query_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `query_history` (
  `query_id` int NOT NULL AUTO_INCREMENT,
  `query_text` text NOT NULL,
  `execution_time_ms` decimal(12,3) DEFAULT NULL,
  `status` varchar(20) NOT NULL,
  `rows_returned` int DEFAULT '0',
  `error_message` text,
  `executed_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`query_id`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `query_history`
--

LOCK TABLES `query_history` WRITE;
/*!40000 ALTER TABLE `query_history` DISABLE KEYS */;
INSERT INTO `query_history` VALUES (1,'select * from workload',8.155,'FAILED',0,'1146 (42S02): Table \'sysnexa.workload\' doesn\'t exist','2026-11-22 19:27:27'),(2,'select * from workloads',1.555,'SUCCESS',3,NULL,'2026-11-22 19:28:01'),(3,'select * from workloads',2.193,'SUCCESS',3,NULL,'2026-11-22 20:05:00'),(4,'select * from workloads',4.273,'SUCCESS',6,NULL,'2026-11-23 19:10:14'),(5,'select * from workloads',4.379,'SUCCESS',6,NULL,'2026-11-23 19:10:14'),(6,'SELECT * FROM resource_history',3.992,'SUCCESS',43,NULL,'2026-11-23 19:46:24'),(7,'SELECT * FROM execution_history',3.430,'SUCCESS',18,NULL,'2026-11-23 19:47:02'),(8,'SELECT * FROM execution_history',2.794,'SUCCESS',18,NULL,'2026-11-23 19:47:07'),(9,'SELECT * FROM execution_history',3.037,'SUCCESS',18,NULL,'2026-11-23 19:47:08'),(10,'select * from workloads',4.071,'SUCCESS',29,NULL,'2026-11-24 19:53:07'),(11,'SELECT COUNT(*) FROM transaction_demo',73.834,'SUCCESS',1,NULL,'2026-11-24 21:28:40'),(12,'SELECT COUNT(*) AS total_records\nFROM transaction_demo',31.026,'SUCCESS',1,NULL,'2026-11-24 21:29:49'),(13,'SELECT COUNT(*) AS total_records\nFROM transaction_demo',25.258,'SUCCESS',1,NULL,'2026-11-24 21:29:52'),(14,'SELECT TABLE_NAME, ENGINE\nFROM information_schema.TABLES\nWHERE TABLE_SCHEMA = \'sysnexa\'\nAND TABLE_NAME IN (\n    \'workloads\',\n    \'execution_history\',\n    \'transaction_demo\'\n)',798.089,'SUCCESS',3,NULL,'2026-11-25 03:31:03'),(15,'SELECT COUNT(DISTINCT SUBSTRING_INDEX(demo_id, \'-\', 2))\nAS total_committed_transactions\nFROM transaction_demo',45.563,'SUCCESS',1,NULL,'2026-11-25 03:41:59'),(16,'SELECT * FROM workload_transaction_history',23.871,'SUCCESS',0,NULL,'2026-11-25 04:09:14'),(17,'SELECT * FROM workload_transaction_history',35.304,'SUCCESS',0,NULL,'2026-11-25 04:10:35'),(18,'SELECT *\nFROM execution_history\nORDER BY execution_id DESC\nLIMIT 5',23.483,'SUCCESS',5,NULL,'2026-11-25 04:10:55'),(19,'select* from workloads',32.140,'SUCCESS',39,NULL,'2026-11-25 04:19:53'),(20,'select * from workloads',30.183,'SUCCESS',39,NULL,'2026-11-25 04:20:47'),(21,'select * from workloads',28.088,'SUCCESS',39,NULL,'2026-11-25 04:20:50'),(22,'select * from workloads',32.105,'SUCCESS',39,NULL,'2026-11-25 04:20:51'),(23,'select * from workloads',22.608,'SUCCESS',39,NULL,'2026-11-25 04:20:51'),(24,'select * from workloads',26.745,'SUCCESS',39,NULL,'2026-11-25 04:20:51');
/*!40000 ALTER TABLE `query_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `resource_history`
--

DROP TABLE IF EXISTS `resource_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `resource_history` (
  `reading_id` bigint NOT NULL AUTO_INCREMENT,
  `cpu_percent` decimal(5,2) DEFAULT NULL,
  `memory_percent` decimal(5,2) DEFAULT NULL,
  `disk_percent` decimal(5,2) DEFAULT NULL,
  `recorded_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`reading_id`)
) ENGINE=InnoDB AUTO_INCREMENT=83 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `resource_history`
--

LOCK TABLES `resource_history` WRITE;
/*!40000 ALTER TABLE `resource_history` DISABLE KEYS */;
INSERT INTO `resource_history` VALUES (1,17.20,90.00,43.50,'2026-11-22 19:28:33'),(2,7.62,12.70,5.43,'2026-11-23 19:08:57'),(3,4.83,12.72,5.43,'2026-11-23 19:08:57'),(4,4.49,12.74,5.43,'2026-11-23 19:08:57'),(5,1.50,12.95,5.43,'2026-11-23 19:09:01'),(6,0.33,12.56,5.43,'2026-11-23 19:09:01'),(7,0.00,12.63,5.43,'2026-11-23 19:09:01'),(8,1.34,12.46,5.43,'2026-11-23 19:09:06'),(9,0.00,12.50,5.43,'2026-11-23 19:09:06'),(10,0.50,12.47,5.43,'2026-11-23 19:09:06'),(11,4.49,13.10,5.43,'2026-11-23 19:18:36'),(12,2.83,13.13,5.43,'2026-11-23 19:18:36'),(13,2.67,13.19,5.43,'2026-11-23 19:18:36'),(14,2.50,13.20,5.43,'2026-11-23 19:18:36'),(15,2.67,12.86,5.43,'2026-11-23 19:18:36'),(16,3.83,12.83,5.43,'2026-11-23 19:18:45'),(17,3.00,12.77,5.43,'2026-11-23 19:18:45'),(18,2.50,12.78,5.43,'2026-11-23 19:18:45'),(19,2.83,12.81,5.43,'2026-11-23 19:18:45'),(20,2.67,12.77,5.43,'2026-11-23 19:18:45'),(21,3.83,12.83,5.43,'2026-11-23 19:18:53'),(22,2.66,12.88,5.43,'2026-11-23 19:18:53'),(23,2.51,12.82,5.43,'2026-11-23 19:18:53'),(24,2.66,12.80,5.43,'2026-11-23 19:18:53'),(25,2.50,12.83,5.43,'2026-11-23 19:18:53'),(26,3.84,12.80,5.43,'2026-11-23 19:40:07'),(27,2.67,12.80,5.43,'2026-11-23 19:40:07'),(28,4.31,12.89,5.43,'2026-11-23 19:40:10'),(29,3.49,12.41,5.43,'2026-11-23 19:40:10'),(30,4.00,12.50,5.43,'2026-11-23 19:40:14'),(31,2.51,12.55,5.43,'2026-11-23 19:40:14'),(32,4.68,12.72,5.43,'2026-11-23 19:43:47'),(33,4.65,12.74,5.43,'2026-11-23 19:43:47'),(34,5.00,12.76,5.43,'2026-11-23 19:43:51'),(35,4.67,12.79,5.43,'2026-11-23 19:43:51'),(36,4.84,12.44,5.43,'2026-11-23 19:43:54'),(37,4.50,12.39,5.43,'2026-11-23 19:43:54'),(38,6.12,12.76,5.43,'2026-11-23 19:45:39'),(39,4.66,12.72,5.43,'2026-11-23 19:45:39'),(40,3.83,12.92,5.43,'2026-11-23 19:45:43'),(41,3.49,12.51,5.43,'2026-11-23 19:45:43'),(42,1.83,12.54,5.43,'2026-11-23 19:45:46'),(43,0.00,12.61,5.43,'2026-11-23 19:45:46'),(44,27.80,89.40,43.20,'2026-11-23 19:55:56'),(45,5.32,12.11,5.43,'2026-11-23 19:56:06'),(46,4.00,12.14,5.43,'2026-11-23 19:56:06'),(47,5.32,12.13,5.43,'2026-11-23 19:56:39'),(48,4.69,12.16,5.43,'2026-11-23 19:56:39'),(49,4.84,12.20,5.43,'2026-11-23 19:56:42'),(50,4.17,12.30,5.43,'2026-11-23 19:56:42'),(51,14.10,90.00,43.20,'2026-11-23 19:57:59'),(52,24.70,89.10,43.20,'2026-11-23 19:58:05'),(53,0.00,12.05,5.43,'2026-11-24 18:18:23'),(54,0.00,12.02,5.43,'2026-11-24 18:18:26'),(55,0.00,12.52,5.43,'2026-11-24 18:18:53'),(56,0.00,12.57,5.43,'2026-11-24 18:18:55'),(57,5.14,12.13,5.43,'2026-11-24 18:19:07'),(58,4.83,12.20,5.43,'2026-11-24 18:19:07'),(59,5.31,12.23,5.43,'2026-11-24 18:19:10'),(60,4.17,12.24,5.43,'2026-11-24 18:19:10'),(61,5.15,12.24,5.43,'2026-11-24 18:19:13'),(62,4.34,12.28,5.43,'2026-11-24 18:19:13'),(63,0.00,12.36,5.43,'2026-11-24 18:19:46'),(64,0.50,12.32,5.43,'2026-11-24 19:20:49'),(65,0.00,11.63,5.43,'2026-11-24 19:38:05'),(66,0.17,13.00,5.43,'2026-11-25 04:01:10'),(67,0.33,12.42,5.43,'2026-11-25 04:02:50'),(68,0.00,11.88,5.43,'2026-11-25 04:03:00'),(69,0.17,13.06,5.43,'2026-11-25 04:25:05'),(70,0.00,11.61,5.43,'2026-11-25 04:48:24'),(71,14.36,13.82,5.43,'2026-11-25 04:49:22'),(72,14.48,13.82,5.43,'2026-11-25 04:49:22'),(73,12.17,13.87,5.43,'2026-11-25 04:49:22'),(74,12.17,13.87,5.43,'2026-11-25 04:49:22'),(75,14.33,13.82,5.43,'2026-11-25 04:49:22'),(76,12.31,13.87,5.43,'2026-11-25 04:49:22'),(77,0.00,13.11,5.43,'2026-11-25 04:50:28'),(78,0.67,12.44,5.43,'2026-11-25 04:50:36'),(79,0.33,12.46,5.43,'2026-11-25 04:59:23'),(80,0.00,12.08,5.43,'2026-11-25 04:59:27'),(81,0.00,11.78,5.43,'2026-11-25 04:59:30'),(82,0.00,11.81,5.43,'2026-11-25 05:59:44');
/*!40000 ALTER TABLE `resource_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `transaction_demo`
--

DROP TABLE IF EXISTS `transaction_demo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `transaction_demo` (
  `demo_id` varchar(100) NOT NULL,
  `description` varchar(200) NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`demo_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `transaction_demo`
--

LOCK TABLES `transaction_demo` WRITE;
/*!40000 ALTER TABLE `transaction_demo` DISABLE KEYS */;
INSERT INTO `transaction_demo` VALUES ('TXN-12218a5f1b7040c1af35d72d79677ba5-1','First transaction operation','2026-11-25 04:00:55'),('TXN-12218a5f1b7040c1af35d72d79677ba5-2','Second transaction operation','2026-11-25 04:00:55'),('TXN-3c6f054a1c6243f1b512065e4db6dc61-1','First transaction operation','2026-11-25 04:00:54'),('TXN-3c6f054a1c6243f1b512065e4db6dc61-2','Second transaction operation','2026-11-25 04:00:54'),('TXN-40817392fe5d4603ae1c9bedc41533e3-1','First transaction operation','2026-11-24 21:35:55'),('TXN-40817392fe5d4603ae1c9bedc41533e3-2','Second transaction operation','2026-11-24 21:35:55'),('TXN-59483d6a5a66477c9e2b28f503b7df61-1','First transaction operation','2026-11-24 21:30:01'),('TXN-59483d6a5a66477c9e2b28f503b7df61-2','Second transaction operation','2026-11-24 21:30:01'),('TXN-97fdfe764bdf4d32bad557fe4f90055d-1','First transaction operation','2026-11-25 04:00:45'),('TXN-97fdfe764bdf4d32bad557fe4f90055d-2','Second transaction operation','2026-11-25 04:00:45'),('TXN-b273acef77324cb4a5b00710859911db-1','First transaction operation','2026-11-25 04:00:42'),('TXN-b273acef77324cb4a5b00710859911db-2','Second transaction operation','2026-11-25 04:00:42'),('TXN-cba442f658884156aa956e421de57c13-1','First transaction operation','2026-11-24 21:41:49'),('TXN-cba442f658884156aa956e421de57c13-2','Second transaction operation','2026-11-24 21:41:49'),('TXN-e0c3404760a849b191a5e1604c99213c-1','First transaction operation','2026-11-25 03:58:19'),('TXN-e0c3404760a849b191a5e1604c99213c-2','Second transaction operation','2026-11-25 03:58:19'),('TXN-e6f35f48cb4c43fba4a99b089ceb8863-1','First transaction operation','2026-11-25 04:04:26'),('TXN-e6f35f48cb4c43fba4a99b089ceb8863-2','Second transaction operation','2026-11-25 04:04:26'),('TXN-ea9d5ff4edfe454f9e38eeef7646710d-1','First transaction operation','2026-11-25 04:00:52'),('TXN-ea9d5ff4edfe454f9e38eeef7646710d-2','Second transaction operation','2026-11-25 04:00:52'),('TXN-ec1b92f111ee4627bd88b4b22429e861-1','First transaction operation','2026-11-25 03:32:08'),('TXN-ec1b92f111ee4627bd88b4b22429e861-2','Second transaction operation','2026-11-25 03:32:08'),('TXN-f64cb2992b624a1493715db065b8595e-1','First transaction operation','2026-11-24 21:24:12'),('TXN-f64cb2992b624a1493715db065b8595e-2','Second transaction operation','2026-11-24 21:24:12'),('TXN-fdaf60fae8d4490d98a520019b8c1029-1','First transaction operation','2026-11-24 21:30:05'),('TXN-fdaf60fae8d4490d98a520019b8c1029-2','Second transaction operation','2026-11-24 21:30:05');
/*!40000 ALTER TABLE `transaction_demo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `workload_transaction_history`
--

DROP TABLE IF EXISTS `workload_transaction_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `workload_transaction_history` (
  `transaction_id` varchar(100) NOT NULL,
  `task_id` varchar(100) NOT NULL,
  `workload_name` varchar(150) DEFAULT NULL,
  `workload_type` varchar(50) DEFAULT NULL,
  `execution_id` int DEFAULT NULL,
  `transaction_status` varchar(30) NOT NULL,
  `workload_status` varchar(30) DEFAULT NULL,
  `error_message` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`transaction_id`),
  KEY `idx_transaction_task` (`task_id`),
  KEY `idx_transaction_status` (`transaction_status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `workload_transaction_history`
--

LOCK TABLES `workload_transaction_history` WRITE;
/*!40000 ALTER TABLE `workload_transaction_history` DISABLE KEYS */;
/*!40000 ALTER TABLE `workload_transaction_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `workloads`
--

DROP TABLE IF EXISTS `workloads`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `workloads` (
  `task_id` varchar(100) NOT NULL,
  `workload_name` varchar(150) NOT NULL,
  `workload_type` varchar(50) DEFAULT NULL,
  `priority` int DEFAULT '1',
  `status` varchar(30) DEFAULT 'READY',
  `submitted_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`task_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `workloads`
--

LOCK TABLES `workloads` WRITE;
/*!40000 ALTER TABLE `workloads` DISABLE KEYS */;
INSERT INTO `workloads` VALUES ('SIM-20261124003840-13b1282e','Simulator CPU Load 1','python',1,'COMPLETED','2026-11-23 19:08:40'),('SIM-20261124003840-1fba4af1','Simulator Memory Load 2','python',2,'COMPLETED','2026-11-23 19:08:40'),('SIM-20261124003840-687709f5','Simulator Disk Load 3','python',3,'COMPLETED','2026-11-23 19:08:40'),('SIM-20261124004816-60c9a206','Simulator Combined Load 3','python',3,'COMPLETED','2026-11-23 19:18:16'),('SIM-20261124004816-ad0aec26','Simulator Combined Load 1','python',1,'COMPLETED','2026-11-23 19:18:16'),('SIM-20261124004816-da290819','Simulator Combined Load 2','python',2,'COMPLETED','2026-11-23 19:18:16'),('SIM-20261124010930-39050400','Simulator Combined Load 3','python',3,'COMPLETED','2026-11-23 19:39:30'),('SIM-20261124010930-af38ecfa','Simulator Combined Load 2','python',2,'COMPLETED','2026-11-23 19:39:30'),('SIM-20261124010930-c01ca372','Simulator Combined Load 1','python',1,'COMPLETED','2026-11-23 19:39:30'),('SIM-20261124011334-1a981d08','Simulator CPU Load 2','python',2,'COMPLETED','2026-11-23 19:43:34'),('SIM-20261124011334-9c62fa09','Simulator CPU Load 1','python',1,'COMPLETED','2026-11-23 19:43:34'),('SIM-20261124011334-f719f2ad','Simulator CPU Load 3','python',3,'COMPLETED','2026-11-23 19:43:34'),('SIM-20261124011525-2c3e1b0f','Simulator Combined Load 2','python',2,'COMPLETED','2026-11-23 19:45:25'),('SIM-20261124011525-47ac681f','Simulator Memory Load 3','python',3,'COMPLETED','2026-11-23 19:45:25'),('SIM-20261124011525-8b0af6d6','Simulator CPU Load 1','python',1,'COMPLETED','2026-11-23 19:45:25'),('SIM-20261124012044-b1c90f16','Simulator CPU Load 1','python',1,'READY','2026-11-23 19:50:45'),('SIM-20261124012045-a78f0f2e','Simulator CPU Load 2','python',2,'READY','2026-11-23 19:50:45'),('SIM-20261124012045-ebb03bcc','Simulator CPU Load 3','python',3,'READY','2026-11-23 19:50:45'),('SIM-20261124012536-2263e124','Simulator CPU Load 2','python',2,'COMPLETED','2026-11-23 19:55:36'),('SIM-20261124012536-a54fa7ca','Simulator CPU Load 1','python',1,'COMPLETED','2026-11-23 19:55:36'),('SIM-20261124012536-b642557f','Simulator CPU Load 3','python',3,'COMPLETED','2026-11-23 19:55:36'),('SIM-20261124234801-491ce16f','Simulator CPU Load 2','python',2,'COMPLETED','2026-11-24 18:18:01'),('SIM-20261124234801-7bcb5152','Simulator CPU Load 3','python',3,'COMPLETED','2026-11-24 18:18:01'),('SIM-20261124234801-df3d0a4d','Simulator CPU Load 1','python',1,'COMPLETED','2026-11-24 18:18:01'),('SIM-20261125025904-12e09c52','Simulator CPU Load 2','python',2,'FAILED','2026-11-24 21:29:04'),('SIM-20261125025904-4eb4e7ca','Simulator CPU Load 1','python',1,'FAILED','2026-11-24 21:29:04'),('SIM-20261125025904-e0bfd0ab','Simulator CPU Load 3','python',3,'FAILED','2026-11-24 21:29:04'),('SIM-20261125030437-2f828b11','Simulator CPU Load 2','python',2,'READY','2026-11-24 21:34:37'),('SIM-20261125030437-3ee7691f','Simulator CPU Load 3','python',3,'READY','2026-11-24 21:34:37'),('SIM-20261125030437-7abdbb4e','Simulator CPU Load 1','python',1,'READY','2026-11-24 21:34:37'),('SIM-20261125092935-448bc4e6','Simulator CPU Load 3','python',3,'READY','2026-11-25 03:59:35'),('SIM-20261125092935-7255af23','Simulator CPU Load 1','python',1,'READY','2026-11-25 03:59:35'),('SIM-20261125092935-b62734cc','Simulator CPU Load 2','python',2,'READY','2026-11-25 03:59:35'),('SIM-20261125094903-cf4c5803','Simulator CPU Load 1','python',1,'READY','2026-11-25 04:19:03'),('SIM-20261125101910-26ee58ed','Simulator CPU Load 3','python',3,'COMPLETED','2026-11-25 04:49:11'),('SIM-20261125101910-ad282541','Simulator CPU Load 1','python',1,'COMPLETED','2026-11-25 04:49:10'),('SIM-20261125101910-c8673b59','Simulator CPU Load 2','python',2,'COMPLETED','2026-11-25 04:49:10'),('TASK-20261123005417337555','calculation  2 5','python',2,'COMPLETED','2026-11-22 19:24:17'),('TASK-20261123005511866523','short task 3 1','python',3,'COMPLETED','2026-11-22 19:25:11'),('TASK-20261123005602604277','urgent task  1 2','python',2,'COMPLETED','2026-11-22 19:26:02'),('TASK-20261125010713095409','uplad tes 1','file_transfer',2,'COMPLETED','2026-11-24 19:37:13'),('TASK-20261125012122527669','heloo','sql',2,'READY','2026-11-24 19:51:22'),('TASK-20261125114218577734','sample','file_transfer',1,'COMPLETED','2026-11-25 06:12:18'),('TASK-20261125123504480542','calc','python',2,'READY','2026-11-25 07:05:04');
/*!40000 ALTER TABLE `workloads` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-11-25 14:57:17
