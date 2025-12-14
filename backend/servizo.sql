CREATE DATABASE  IF NOT EXISTS `servizo` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `servizo`;
-- MySQL dump 10.13  Distrib 8.0.44, for Win64 (x86_64)
--
-- Host: localhost    Database: servizo
-- ------------------------------------------------------
-- Server version	8.0.44

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `admin`
--

DROP TABLE IF EXISTS `admin`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin` (
  `AdminID` int NOT NULL AUTO_INCREMENT,
  `Name` varchar(100) NOT NULL,
  `Email` varchar(100) NOT NULL,
  `Password` varchar(255) NOT NULL,
  PRIMARY KEY (`AdminID`),
  UNIQUE KEY `Email` (`Email`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin`
--

LOCK TABLES `admin` WRITE;
/*!40000 ALTER TABLE `admin` DISABLE KEYS */;
INSERT INTO `admin` VALUES (1,'Admin','admin@gmail.com','scrypt:32768:8:1$9INLuLEJJ8VSjGjJ$00c8ffcb3a2b170f44b000c8cd0902cf317cfd139be6dfb97dcd72fab3732c796be36c5cc9d9e14f39c5023eac6712ef6d8ae842ab92ad4eb0ef34b655381d7c');
/*!40000 ALTER TABLE `admin` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `booking`
--

DROP TABLE IF EXISTS `booking`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `booking` (
  `BookingID` int NOT NULL AUTO_INCREMENT,
  `OfferID` int NOT NULL,
  `CustomerID` int NOT NULL,
  `ServiceProviderID` int NOT NULL,
  `ServiceID` int NOT NULL,
  `BookingDate` date NOT NULL,
  `BookingTime` time NOT NULL,
  `FinalAmount` decimal(10,2) NOT NULL,
  `Status` enum('Scheduled','In Progress','Completed','Incomplete','Cancelled') DEFAULT 'Scheduled',
  `ProviderConfirmedComplete` tinyint(1) DEFAULT '0',
  `CustomerConfirmedComplete` tinyint(1) DEFAULT '0',
  `RefundStatus` varchar(20) DEFAULT NULL,
  `ProviderPaymentStatus` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`BookingID`),
  KEY `OfferID` (`OfferID`),
  KEY `CustomerID` (`CustomerID`),
  KEY `ServiceProviderID` (`ServiceProviderID`),
  KEY `ServiceID` (`ServiceID`),
  CONSTRAINT `booking_ibfk_1` FOREIGN KEY (`OfferID`) REFERENCES `offers` (`OfferID`),
  CONSTRAINT `booking_ibfk_2` FOREIGN KEY (`CustomerID`) REFERENCES `customer` (`CustomerID`),
  CONSTRAINT `booking_ibfk_3` FOREIGN KEY (`ServiceProviderID`) REFERENCES `serviceprovider` (`ServiceProviderID`),
  CONSTRAINT `booking_ibfk_4` FOREIGN KEY (`ServiceID`) REFERENCES `service` (`ServiceID`)
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `booking`
--

LOCK TABLES `booking` WRITE;
/*!40000 ALTER TABLE `booking` DISABLE KEYS */;
INSERT INTO `booking` VALUES (1,1,1,5,1,'2025-11-12','00:25:00',800.00,'Completed',0,0,NULL,'Paid'),(2,2,1,5,1,'2025-11-12','01:05:00',800.00,'Completed',0,0,NULL,NULL),(3,3,1,5,1,'2025-11-12','09:49:00',900.00,'Completed',0,0,NULL,NULL),(4,4,1,5,1,'2025-11-12','10:15:00',800.00,'Completed',0,0,NULL,'Paid'),(5,5,1,5,1,'2025-11-16','22:45:00',1500.00,'Scheduled',0,1,NULL,NULL),(6,6,1,1,2,'2025-11-16','11:55:00',1200.00,'Incomplete',0,1,'Pending',NULL),(7,9,1,5,1,'2025-11-19','15:18:00',2000.00,'Incomplete',0,0,'Pending',NULL),(8,10,2,1,2,'2025-11-21','14:55:00',1900.00,'Scheduled',0,1,NULL,NULL),(9,11,2,5,1,'2025-11-18','03:35:00',1600.00,'Scheduled',1,0,NULL,NULL),(10,12,1,5,1,'2025-11-25','12:00:00',2000.00,'Incomplete',0,0,'Approved',NULL),(11,13,2,1,2,'2025-11-18','13:26:00',2000.00,'Incomplete',0,0,'Approved',NULL),(12,14,3,1,2,'2025-11-18','13:07:00',800.00,'Incomplete',0,0,'Approved',NULL),(13,15,1,5,1,'2025-11-28','15:20:00',3000.00,'Incomplete',0,0,'Approved',NULL),(14,16,1,5,1,'2025-11-27','15:00:00',1500.00,'Cancelled',0,0,'Approved',NULL),(15,20,3,17,4,'2025-11-19','01:50:00',700.00,'Completed',1,1,NULL,'Pending'),(16,21,2,15,5,'2025-11-29','01:25:00',700.00,'Scheduled',0,0,NULL,NULL),(17,22,2,16,6,'2025-11-29','01:59:00',3000.00,'Scheduled',0,0,NULL,NULL),(18,23,3,17,4,'2025-11-22','02:09:00',500.00,'Scheduled',0,0,NULL,NULL),(19,24,1,16,6,'2025-11-22','02:14:00',4000.00,'Completed',1,1,NULL,'Pending');
/*!40000 ALTER TABLE `booking` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `commission`
--

DROP TABLE IF EXISTS `commission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `commission` (
  `CommissionID` int NOT NULL AUTO_INCREMENT,
  `PaymentID` int DEFAULT NULL,
  `AdminID` int DEFAULT NULL,
  `Percentage` decimal(5,2) DEFAULT NULL,
  `Amount` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`CommissionID`),
  KEY `PaymentID` (`PaymentID`),
  KEY `AdminID` (`AdminID`),
  CONSTRAINT `commission_ibfk_1` FOREIGN KEY (`PaymentID`) REFERENCES `payment` (`PaymentID`),
  CONSTRAINT `commission_ibfk_2` FOREIGN KEY (`AdminID`) REFERENCES `admin` (`AdminID`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `commission`
--

LOCK TABLES `commission` WRITE;
/*!40000 ALTER TABLE `commission` DISABLE KEYS */;
/*!40000 ALTER TABLE `commission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `customer`
--

DROP TABLE IF EXISTS `customer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `customer` (
  `CustomerID` int NOT NULL AUTO_INCREMENT,
  `Name` varchar(100) NOT NULL,
  `Email` varchar(100) NOT NULL,
  `PhoneNo` varchar(15) DEFAULT NULL,
  `Address` varchar(255) DEFAULT NULL,
  `Password` varchar(255) NOT NULL,
  PRIMARY KEY (`CustomerID`),
  UNIQUE KEY `Email` (`Email`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `customer`
--

LOCK TABLES `customer` WRITE;
/*!40000 ALTER TABLE `customer` DISABLE KEYS */;
INSERT INTO `customer` VALUES (1,'Hameed Khan','hameed@gmail.com','03331942111','Gulshan, Karachi','scrypt:32768:8:1$QBTW6bURGDQzYtNJ$45e68443d204a87a58eaa4f631a5db049f3d4a07db96a92032f069c5a8e32386d036f6f2451a1dd012737798426ea72b25bb64400903e4c84efa0b35773e6dd6'),(2,'Aaban Asif','aaban@gmail.com','03331942761','Saddar, Karachi','scrypt:32768:8:1$N2dRKxDWfzAaK1FS$118e3be077f25883f46208770e1212dd12b0632283a22e83c3f427b12180da109fdb39653ee30d393ce4fa55321fa70387dd2b1230f4d430716567c9f9794362'),(3,'Azka Hassan','azka@gmail.com','03331988772','North Karachi','scrypt:32768:8:1$qAmlXr1uqcYwm7sw$9c7deb4c2dce94f4ec3c38f33acf178b01f26ec6a41eb0e1ae35d9cb70831c9b48ad98956f70fffa765be8b3856d7cb97c92148578cf49b49c20132d0b540746');
/*!40000 ALTER TABLE `customer` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `feedback`
--

DROP TABLE IF EXISTS `feedback`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `feedback` (
  `FeedbackID` int NOT NULL AUTO_INCREMENT,
  `CustomerID` int DEFAULT NULL,
  `ServiceProviderID` int DEFAULT NULL,
  `BookingID` int DEFAULT NULL,
  `Text` varchar(300) DEFAULT NULL,
  `Rating` int DEFAULT NULL,
  `FeedbackDate` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`FeedbackID`),
  KEY `CustomerID` (`CustomerID`),
  KEY `ServiceProviderID` (`ServiceProviderID`),
  KEY `BookingID` (`BookingID`),
  CONSTRAINT `feedback_ibfk_1` FOREIGN KEY (`CustomerID`) REFERENCES `customer` (`CustomerID`),
  CONSTRAINT `feedback_ibfk_2` FOREIGN KEY (`ServiceProviderID`) REFERENCES `serviceprovider` (`ServiceProviderID`),
  CONSTRAINT `feedback_ibfk_3` FOREIGN KEY (`BookingID`) REFERENCES `booking` (`BookingID`),
  CONSTRAINT `feedback_chk_1` CHECK ((`Rating` between 1 and 5))
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `feedback`
--

LOCK TABLES `feedback` WRITE;
/*!40000 ALTER TABLE `feedback` DISABLE KEYS */;
INSERT INTO `feedback` VALUES (1,1,5,1,'Excellent Service ',1,'2025-11-11 20:33:58'),(2,1,5,3,'Satisfied with the service. Provider arrived late though',2,'2025-11-16 14:12:37'),(3,1,5,2,'good service',5,'2025-11-16 17:05:04'),(4,3,17,15,'Satisfied with the service!',5,'2025-11-18 21:34:58');
/*!40000 ALTER TABLE `feedback` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `messages`
--

DROP TABLE IF EXISTS `messages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `messages` (
  `MessageID` int NOT NULL AUTO_INCREMENT,
  `OfferID` int NOT NULL,
  `SenderID` int NOT NULL,
  `SenderRole` enum('customer','provider') NOT NULL,
  `Message` text NOT NULL,
  `Timestamp` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`MessageID`),
  KEY `OfferID` (`OfferID`),
  CONSTRAINT `messages_ibfk_1` FOREIGN KEY (`OfferID`) REFERENCES `offers` (`OfferID`)
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `messages`
--

LOCK TABLES `messages` WRITE;
/*!40000 ALTER TABLE `messages` DISABLE KEYS */;
INSERT INTO `messages` VALUES (1,7,1,'provider','hi i accepted your offer','2025-11-16 00:26:27'),(2,7,1,'customer','hi cool','2025-11-16 00:27:14'),(3,7,1,'provider','hi','2025-11-16 03:28:06'),(4,6,1,'provider','hi','2025-11-16 03:35:53'),(5,7,1,'provider','how was my service?','2025-11-16 03:39:22'),(6,5,5,'provider','hi','2025-11-16 19:07:50'),(7,5,1,'customer','when will you complete the work?','2025-11-16 19:08:22'),(8,5,5,'provider','around 7 tomorrow','2025-11-16 19:09:13'),(9,8,5,'provider','hi','2025-11-16 23:55:15'),(10,5,5,'provider','?','2025-11-16 23:59:07'),(11,10,1,'provider','hi','2025-11-18 02:54:50'),(12,10,1,'provider','i am willing to accept','2025-11-18 02:54:56'),(13,10,2,'customer','ok','2025-11-18 02:55:35'),(14,10,1,'provider','completed the work','2025-11-18 02:58:36'),(15,14,1,'provider','salam kaam karwana ha?','2025-11-18 12:57:09'),(16,18,5,'provider','hi','2025-11-19 00:23:26'),(17,18,2,'customer','hi','2025-11-19 00:45:56'),(18,20,17,'provider','hi','2025-11-19 01:38:22'),(19,5,1,'customer','theek hay','2025-11-22 17:22:45');
/*!40000 ALTER TABLE `messages` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `offers`
--

DROP TABLE IF EXISTS `offers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `offers` (
  `OfferID` int NOT NULL AUTO_INCREMENT,
  `CustomerID` int NOT NULL,
  `ServiceID` int NOT NULL,
  `OfferedPrice` decimal(10,2) NOT NULL,
  `OfferDate` date NOT NULL,
  `OfferTime` time NOT NULL,
  `Location` varchar(255) DEFAULT NULL,
  `Latitude` decimal(10,6) DEFAULT NULL,
  `Longitude` decimal(10,6) DEFAULT NULL,
  `IssueDescription` text,
  `OfferStatus` enum('Pending','Accepted','Paid','Rejected','Expired') DEFAULT 'Pending',
  `AcceptedProviderID` int DEFAULT NULL,
  `ValidUntil` datetime DEFAULT NULL,
  `ChatStarted` tinyint(1) DEFAULT '0',
  `ChatInitiatorID` int DEFAULT NULL,
  `ChatActive` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`OfferID`),
  KEY `CustomerID` (`CustomerID`),
  KEY `ServiceID` (`ServiceID`),
  CONSTRAINT `offers_ibfk_1` FOREIGN KEY (`CustomerID`) REFERENCES `customer` (`CustomerID`),
  CONSTRAINT `offers_ibfk_2` FOREIGN KEY (`ServiceID`) REFERENCES `service` (`ServiceID`)
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `offers`
--

LOCK TABLES `offers` WRITE;
/*!40000 ALTER TABLE `offers` DISABLE KEYS */;
INSERT INTO `offers` VALUES (1,1,1,800.00,'2025-11-12','00:25:00','Gulshan, University Road, Overseas Cooperative Housing Society, Gulshan-e-Iqbal Town, Gulshan District, Karachi Division, 75300, Pakistan',24.897698,67.066334,'Pipe broke and there is a leakage in the kitchen','Paid',5,'2025-11-12 00:25:00',1,5,1),(2,1,1,800.00,'2025-11-12','01:05:00','Ichhra, Model Town Tehsil, Lahore District, Lahore Division, Punjab, 54357, Pakistan',31.533659,74.316874,'Pipe broke','Paid',5,'2025-11-12 01:05:00',0,NULL,0),(3,1,1,900.00,'2025-11-12','09:49:00','Padri, Lahore Cantonment Tehsil, Lahore District, Lahore Division, Punjab, 53200, Pakistan',31.525856,74.497460,'pipe broked','Paid',5,'2025-11-12 09:49:00',1,5,1),(4,1,1,800.00,'2025-11-12','10:15:00','Gulshan, University Road, Overseas Cooperative Housing Society, Gulshan-e-Iqbal Town, Gulshan District, Karachi Division, 75300, Pakistan',24.897698,67.066334,'pipe broke in house','Paid',5,'2025-11-12 10:15:00',1,5,1),(5,1,1,1500.00,'2025-11-16','22:45:00','Gulshan, University Road, Overseas Cooperative Housing Society, Gulshan-e-Iqbal Town, Gulshan District, Karachi Division, 75300, Pakistan',24.897698,67.066334,'Pipe not working and leaking','Paid',5,'2025-11-16 22:45:00',1,5,1),(6,1,2,1200.00,'2025-11-16','11:55:00','FB Area Block 18, FB Area, Nazimabad District, Karachi Division, Pakistan',24.945812,67.072695,'Extension wire not working','Paid',1,'2025-11-16 11:55:00',1,1,1),(7,1,2,1600.00,'2025-11-17','00:26:00','Gulshan, Gulshan e Iqbal Block 5, Gulshan-e-Iqbal Block 5, Gulshan-e-Iqbal Town, Gulshan District, Karachi Division, 75300, Pakistan',24.920835,67.088075,'Wire spark','Expired',NULL,'2025-11-17 00:26:00',1,1,1),(8,1,1,1700.00,'2025-11-17','23:49:00','FB Area, Nazimabad District, Karachi Division, Sindh, 75950, Pakistan',24.932569,67.070392,'pipe not working','Expired',NULL,'2025-11-17 23:49:00',1,5,1),(9,1,1,2000.00,'2025-11-19','15:18:00','Gulshan, University Road, Overseas Cooperative Housing Society, Gulshan-e-Iqbal Town, Gulshan District, Karachi Division, 75300, Pakistan',24.897698,67.066334,'Pipe broke again','Paid',5,'2025-11-19 15:18:00',1,5,1),(10,2,2,1900.00,'2025-11-21','14:55:00','Saddar Town, Karachi District, Karachi Division, Sindh, Pakistan',24.860571,67.031741,'Extenstion not working','Paid',1,'2025-11-21 14:55:00',1,1,1),(11,2,1,1600.00,'2025-11-18','03:35:00','Saddar Town, Karachi District, Karachi Division, Sindh, Pakistan',24.860571,67.031741,'pipe not working','Paid',5,'2025-11-18 03:35:00',0,NULL,0),(12,1,1,2000.00,'2025-11-25','12:00:00','Lahore Cantonment, Lahore Cantonment Tehsil, Lahore District, Lahore Division, Punjab, 54810, Pakistan',31.522069,74.379330,'Fix leak, broken pipe','Paid',5,'2025-11-25 12:00:00',0,NULL,0),(13,2,2,2000.00,'2025-11-18','13:26:00','Mall Road, Saint John Park, Upper Mall, Lahore, Lahore Cantonment Tehsil, Lahore District, Lahore Division, Punjab, 54100, Pakistan',31.532897,74.364223,'wire problem','Paid',1,'2025-11-18 13:26:00',0,NULL,0),(14,3,2,800.00,'2025-11-18','13:07:00','Saint John Park, Lahore Cantonment, Lahore Cantonment Tehsil, Lahore District, Lahore Division, Punjab, 54100, Pakistan',31.525581,74.367657,'wire issue again','Paid',1,'2025-11-18 13:07:00',1,1,1),(15,1,1,3000.00,'2025-11-28','15:20:00','Chaudhary Ali Anwar Road, Muslim Town, Model Town Tehsil, Lahore District, Lahore Division, Punjab, 54357, Pakistan',31.511386,74.315000,'fix leak, brocken pipe','Paid',5,'2025-11-28 15:20:00',0,NULL,0),(16,1,1,1500.00,'2025-11-27','15:00:00','Shadman Colony, Shadman, Model Town Tehsil, Lahore District, Lahore Division, Punjab, 57760, Pakistan',31.537871,74.330921,'fix broken pipe','Paid',5,'2025-11-27 15:00:00',0,NULL,0),(17,2,1,1500.00,'2025-11-19','23:24:00','Shah Jamal, Model Town Tehsil, Lahore District, Lahore Division, Punjab, 57760, Pakistan',31.524995,74.326115,'pipe issue','Expired',5,'2025-11-19 23:24:00',0,NULL,0),(18,2,1,1900.00,'2025-11-20','18:44:00','FB Area, Nazimabad District, Karachi Division, Sindh, 75950, Pakistan',24.932569,67.070392,'Water Motor not working','Expired',NULL,'2025-11-20 18:44:00',1,5,1),(19,1,1,1600.00,'2025-11-22','20:44:00','Saddar Town, Karachi District, Karachi Division, Sindh, Pakistan',24.860571,67.031741,'Draining piling up','Expired',NULL,'2025-11-22 20:44:00',0,NULL,0),(20,3,4,700.00,'2025-11-19','01:50:00','7B, 3rd Central Lane, DHA Phase 2, Saddar Town, Karachi District, Karachi Division, 75220, Pakistan',24.838153,67.060375,'Deep Cleaning of Kitchen','Paid',17,'2025-11-19 01:50:00',1,17,1),(21,2,5,700.00,'2025-11-29','01:25:00','Bismillah Road, Jacob Lines, Jamshed Town, Gulshan District, Karachi Division, 74400, Pakistan',24.867437,67.036686,'Triminning of plants','Paid',15,'2025-11-29 01:25:00',1,15,1),(22,2,6,3000.00,'2025-11-29','01:59:00','Bizerta Lines, Saddar Town, Karachi District, Karachi Division, 74800, Pakistan',24.856846,67.051105,'Wall Paint in 4 rooms','Paid',16,'2025-11-29 01:59:00',0,NULL,0),(23,3,4,500.00,'2025-11-22','02:09:00','Merchant\'s Store, V2GM+85, Rodriguez Road, Jamshed Town, Gulshan District, Karachi Division, 74550, Pakistan',24.875847,67.032909,'deep cleaning of entire house','Paid',17,'2025-11-22 02:09:00',0,NULL,0),(24,1,6,4000.00,'2025-11-22','02:14:00','146G, PECHS Block 2, Jamshed Town, Gulshan District, Karachi Division, 75100, Pakistan',24.875847,67.055569,'Paint in entire house','Paid',16,'2025-11-22 02:14:00',0,NULL,0),(25,3,5,1500.00,'2025-11-29','19:24:00','Street 114, PECHS Block 2, Jamshed Town, Gulshan District, Karachi Division, Sindh, 75100, Pakistan',24.868994,67.054882,'trimmin of plants','Accepted',15,'2025-11-29 19:24:00',0,NULL,0);
/*!40000 ALTER TABLE `offers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `payment`
--

DROP TABLE IF EXISTS `payment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `payment` (
  `PaymentID` int NOT NULL AUTO_INCREMENT,
  `CustomerID` int DEFAULT NULL,
  `ServiceProviderID` int DEFAULT NULL,
  `OfferID` int DEFAULT NULL,
  `Details` varchar(100) DEFAULT NULL,
  `Amount` decimal(10,2) NOT NULL,
  `PaymentDate` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `Status` enum('Pending','Completed','Refund_Pending','Refunded','Failed') DEFAULT 'Pending',
  `PaymentType` varchar(50) DEFAULT NULL,
  `HeldAmount` decimal(10,2) DEFAULT '0.00',
  PRIMARY KEY (`PaymentID`),
  KEY `CustomerID` (`CustomerID`),
  KEY `ServiceProviderID` (`ServiceProviderID`),
  KEY `OfferID` (`OfferID`),
  CONSTRAINT `payment_ibfk_1` FOREIGN KEY (`CustomerID`) REFERENCES `customer` (`CustomerID`),
  CONSTRAINT `payment_ibfk_2` FOREIGN KEY (`ServiceProviderID`) REFERENCES `serviceprovider` (`ServiceProviderID`),
  CONSTRAINT `payment_ibfk_3` FOREIGN KEY (`OfferID`) REFERENCES `offers` (`OfferID`)
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payment`
--

LOCK TABLES `payment` WRITE;
/*!40000 ALTER TABLE `payment` DISABLE KEYS */;
INSERT INTO `payment` VALUES (1,1,5,1,NULL,800.00,'2025-11-11 19:18:33','Completed',NULL,0.00),(2,1,5,2,NULL,800.00,'2025-11-11 20:00:57','Completed',NULL,0.00),(3,1,5,3,NULL,900.00,'2025-11-12 04:47:56','Completed',NULL,0.00),(4,1,5,4,NULL,800.00,'2025-11-12 05:15:41','Completed',NULL,0.00),(5,1,5,5,NULL,1500.00,'2025-11-15 18:09:30','Completed',NULL,0.00),(6,1,1,6,NULL,1200.00,'2025-11-15 19:16:18','Completed',NULL,0.00),(12,2,1,10,NULL,1900.00,'2025-11-17 21:57:13','Completed',NULL,0.00),(13,2,5,11,NULL,1600.00,'2025-11-17 22:25:20','Completed',NULL,0.00),(14,1,5,12,NULL,2000.00,'2025-11-18 07:17:14','Refunded',NULL,0.00),(15,2,1,13,NULL,2000.00,'2025-11-18 07:27:23','Refunded',NULL,0.00),(16,3,1,14,NULL,800.00,'2025-11-18 07:58:11','Refunded',NULL,0.00),(17,1,5,15,NULL,3000.00,'2025-11-18 10:15:37','Refunded',NULL,0.00),(18,1,5,16,NULL,1500.00,'2025-11-18 10:42:23','Refunded',NULL,0.00),(19,3,17,20,NULL,700.00,'2025-11-18 20:36:27','Completed',NULL,0.00),(20,2,15,21,NULL,700.00,'2025-11-21 20:15:26','Completed',NULL,0.00),(21,2,16,22,NULL,3000.00,'2025-11-21 20:42:15','Completed',NULL,0.00),(22,3,17,23,NULL,500.00,'2025-11-21 20:47:56','Completed',NULL,0.00),(23,1,16,24,NULL,4000.00,'2025-11-21 21:01:08','Completed','Customer_Advance',0.00);
/*!40000 ALTER TABLE `payment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `providerpayouts`
--

DROP TABLE IF EXISTS `providerpayouts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `providerpayouts` (
  `PayoutID` int NOT NULL AUTO_INCREMENT,
  `BookingID` int DEFAULT NULL,
  `ProviderID` int DEFAULT NULL,
  `TotalAmount` decimal(10,2) DEFAULT NULL,
  `ProviderAmount` decimal(10,2) DEFAULT NULL,
  `AdminCommission` decimal(10,2) DEFAULT NULL,
  `StripeTransferID` varchar(255) DEFAULT NULL,
  `Status` enum('Paid','Failed') DEFAULT 'Paid',
  `PaidAt` datetime DEFAULT NULL,
  PRIMARY KEY (`PayoutID`),
  KEY `BookingID` (`BookingID`),
  KEY `ProviderID` (`ProviderID`),
  CONSTRAINT `providerpayouts_ibfk_1` FOREIGN KEY (`BookingID`) REFERENCES `booking` (`BookingID`),
  CONSTRAINT `providerpayouts_ibfk_2` FOREIGN KEY (`ProviderID`) REFERENCES `serviceprovider` (`ServiceProviderID`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `providerpayouts`
--

LOCK TABLES `providerpayouts` WRITE;
/*!40000 ALTER TABLE `providerpayouts` DISABLE KEYS */;
INSERT INTO `providerpayouts` VALUES (1,4,5,800.00,640.00,160.00,NULL,'Paid','2025-11-16 21:18:22'),(2,1,5,800.00,640.00,160.00,NULL,'Paid','2025-11-18 14:35:17');
/*!40000 ALTER TABLE `providerpayouts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `service`
--

DROP TABLE IF EXISTS `service`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `service` (
  `ServiceID` int NOT NULL AUTO_INCREMENT,
  `Name` varchar(100) NOT NULL,
  `Description` varchar(300) DEFAULT NULL,
  `SuggestedPrice` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`ServiceID`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `service`
--

LOCK TABLES `service` WRITE;
/*!40000 ALTER TABLE `service` DISABLE KEYS */;
INSERT INTO `service` VALUES (1,'Plumbing','Quick and clean plumbing repairs and installations.',500.00),(2,'Electrical','Safe and reliable electrical fixes and installations.',700.00),(3,'Carpentry','Custom woodwork and repairs made to fit perfectly.',1500.00),(4,'Cleaner','Spotless, efficient cleaning tailored to your space.',500.00),(5,'Gardener','Healthy, vibrant gardens nurtured with expert care.',800.00),(6,'Painter','Quality paintwork that brings color and life to your home',3000.00);
/*!40000 ALTER TABLE `service` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `serviceprovider`
--

DROP TABLE IF EXISTS `serviceprovider`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `serviceprovider` (
  `ServiceProviderID` int NOT NULL AUTO_INCREMENT,
  `AdminID` int DEFAULT NULL,
  `Name` varchar(100) NOT NULL,
  `Email` varchar(100) NOT NULL,
  `PhoneNo` varchar(15) DEFAULT NULL,
  `CNIC` varchar(20) NOT NULL,
  `Address` varchar(255) DEFAULT NULL,
  `Password` varchar(255) NOT NULL,
  `ValidationStatus` enum('Pending','Approved','Rejected') DEFAULT 'Pending',
  `ServiceCategory` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`ServiceProviderID`),
  UNIQUE KEY `Email` (`Email`),
  UNIQUE KEY `CNIC` (`CNIC`),
  KEY `AdminID` (`AdminID`),
  CONSTRAINT `serviceprovider_ibfk_1` FOREIGN KEY (`AdminID`) REFERENCES `admin` (`AdminID`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `serviceprovider`
--

LOCK TABLES `serviceprovider` WRITE;
/*!40000 ALTER TABLE `serviceprovider` DISABLE KEYS */;
INSERT INTO `serviceprovider` VALUES (1,NULL,'Aslam Siddiqui','aslam@gmail.com','+923331942333','4210128834567','Gulshan, Karachi','scrypt:32768:8:1$N2wtYGTDJupmtDBa$75e7d7d9850712ed007881e23f0dab6a7d323d3464a92e0027bedb627bad2d1da8559bca1f8f9b8243bfbcbfa97de3ab262cc4652606ec904ebe9616d0415a20','Approved','Electrical'),(2,NULL,'Bilal Ahmed','bilal@gmail.com','+923331942444','4210128836721','Karsaz, Karachi','scrypt:32768:8:1$Kur3cD3pmIgOq3QS$bb6c07e66d7d5db213e45479f5bbf892cd93f5130441803f3469d9effaa24082227e38d5c0ab1a3ce0dfaf51c35fe5a6af98cf0ba8d39ff7a1e57a5fa58d6af5','Approved','Carpentry'),(4,NULL,'Noman Siddiqui','noman@gmail.com','+923331942888','4210128836792','FB Area, Karachi','scrypt:32768:8:1$KUxu6ZtkGOMyNWxK$b3aa52b9b02d486d8c978c5c32e979be2f92771a6986a4c30f018136804e94955e92ce37499bbe207f07942166d2bcbd36ac30dee1e6af071c26cdf0ee898fd9','Rejected','Plumbing'),(5,NULL,'Shakeel Ahmed','shakeel@gmail.com','+923331947777','4210128833472','Saddar, Karachi','scrypt:32768:8:1$D82qyxqaELOGtIoC$3c8d7007a316be192faac1489ced40dca0e075fe29f21c6e9fc1d32253746f4aa05083d5118aced5f87ea617f81a31b27d472f4cd39f299e8917df3d4d793f32','Approved','Plumbing'),(6,NULL,'Anfal Asif','anfal@gmail.com','+923331942111','4210128834560','FB Area, Karachi','scrypt:32768:8:1$eRehKTiYpEIjveTx$e368d9689f884ab0af48bd298b711bfc6e61ee7afc652a822367178ebad4436671d347141bc95ddfc7e5495f31f155b335117f76e493ec183ca77ccf16268bfd','Approved','Electrical'),(7,NULL,'Faraz Ahmed','faraz@gmail.com','+92333173331','4210128836890','Karimabad, Karachi','scrypt:32768:8:1$HDGo0JLEepY5BIzE$1816bcb79803bc7fd91dcb2d550e922cef2cf228f8b7221032e62f3afaf416f87f925dab70e14bd89d95c3a45e981ad38fba326df58c886dee7d81d895f12440','Approved','Carpentry'),(8,NULL,'Haris Ali','haris@gmail.com','+923331942983','4210127835711','Gulshan, Karachi','scrypt:32768:8:1$OWatiAvwEgp22J1z$b485938f42f403cc030b0cd2eb256cc3d9cc9b2d18518a550eb4d0b39917c3d935c1a1892b99268987477349cb8000ae29dff2a1a4133a58a09a6e43e937df2e','Pending','Carpentry'),(9,NULL,'Imran Alam','imran@gmail.com','+923331942674','4210128838888','Lyaari, Karachi','scrypt:32768:8:1$XyeA48sBRN1RjVU9$295ed951684fab33722540d4f10041dbc606a884af1fbc9bbe169e6eea54e41ece246fb413da6a809e6f03f0825ba08987787eb1f2f077f701a9b2cc978d6355','Rejected','Electrical'),(10,NULL,'Muzzamil Ali','muzzamil@gmail.com','+923331942234','4210127835757','Samnabad, Karachi','scrypt:32768:8:1$pcBfw6nxNxGkfU0u$441607470b465709f916d5df6bccfd634df99d4894baa43c2c35477bca52a490007e9a720722b68b7b53ca74e0aeb3cde7a88add24eaa20c1f51db7535feee1e','Approved','Electrical'),(11,NULL,'Bashir Farooq','bashir@gmail.com','+923331947865','4210128837982','Machar Colony, Karachi','scrypt:32768:8:1$KyyS1eDUl3FwGjbO$9bc630824315f33ccbd696e8fecc6b6666164ade0c623451b2f4e13bbe9895ad22b4a21003f23c7e3db7f33dabeb6c3021bbba23f1aa3b49cd9d1b9ce2cc3193','Pending','Electrical'),(12,NULL,'Murtaza wahab','murtaza@gmail.com','+923331942983','4210128836893','Korangi, Karachi','scrypt:32768:8:1$KOvBUJx0qrbYx3DV$30c1766d4fdb6e6550fd98161624b11fdb604c9257fef7ecd47a237c625ef2935558fe0cd2acec3ef35e6f1d11f5e461a09394f3208ae0c574f0dabde3c2a3c3','Approved','Electrical'),(13,NULL,'Murad Ali','murad@gmail.com','+923331942775','4210128836799','Sohrab Goth, Karachi','scrypt:32768:8:1$xcVUYeWx7uRE8SJ7$6d5dbc0b800ef305b5cb0c0be4689a7ceaec51b0daef6ae66a240152f60ef754d9cefa6a8e2b24b7cfede50bb1efe36dd5e76a211ac79f38eb8750b4136c0bf9','Approved','Electrical'),(14,NULL,'Bahadur Shah Zafar','bahadur@gmail.com','+923391942881','4210127835750','Safoora Goth, Karachi','scrypt:32768:8:1$WK9NZS4GdecGFQDc$fdcb0435d52fe76dfa3542558f57e7664c45259490dbec2e95fb30ce9bdfef70b6eeb790520877915fae81966baa50be0113f63b487d13adbb40f6fdf0981a3a','Approved','Carpentry'),(15,NULL,'Mohsin Ali','mohsin@gmail.com','+923331947766','4210128836983',' Samnabad Karachi','scrypt:32768:8:1$YZ9BdfwpVovBZe3p$b18e360882b8a4599638a5c8d6a0dddf54757ed0dfd3e6d9bb4b1de81cfef09f68fc5ca3d395a836097d67b2d5a30c265bca5095d3ce288acdbf967c10c3afb5','Approved','Gardener'),(16,NULL,'Abdullah Somroo','abdullah@gmail.com','+923331947774','4210128836880','Maskan, Karachi','scrypt:32768:8:1$KpNfySUfaxOuXr3h$c7150c93746dacc72c8d7328ab42e251a04011261c002c19b858e88607dc3f96fa9370da4d45df599b5881e4fac95ae20b89ad4db4ac269e784f413d37ea4cc7','Approved','Painter'),(17,NULL,'Sadiq Fazal','sadiq@gmail.com','+923331942776','4210128836883','Numaish, Karachi','scrypt:32768:8:1$gSwmYanxPdAZdW9r$f36e3491b73064529ef8ed1edcadc3502fe020c070c9e504cf405aed3357f2ba2d351eecff12eb650b11083474957237265bfb035e7ae1a65ae615a309f8f1bf','Approved','Cleaner');
/*!40000 ALTER TABLE `serviceprovider` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-11-22 21:14:38
