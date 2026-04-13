--
-- Table structure for table `sp_category`
--

DROP TABLE IF EXISTS `sp_category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sp_category` (
  `cat_id` int NOT NULL AUTO_INCREMENT,
  `cat_name` varchar(30) NOT NULL,
  `cat_acronym` varchar(15) NOT NULL,
  `is_static_fg` tinyint DEFAULT NULL,
  `is_active_fg` tinyint DEFAULT NULL,
  `cat_yaxis_unit` varchar(75) DEFAULT NULL,
  `cat_yaxis_divisor` int DEFAULT NULL,
  `add_interval_fg` tinyint DEFAULT NULL,
  `gen_summary` tinyint DEFAULT NULL,
  PRIMARY KEY (`cat_id`)
) ENGINE=InnoDB AUTO_INCREMENT=44 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sp_client`
--

DROP TABLE IF EXISTS `sp_client`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sp_client` (
  `cl_id` int NOT NULL AUTO_INCREMENT,
  `cl_name` varchar(30) NOT NULL,
  `cl_shortname` varchar(15) NOT NULL,
  `cl_creation_date` datetime NOT NULL,
  `is_active_fg` tinyint DEFAULT NULL,
  `cl_account_contact` varchar(30) DEFAULT NULL,
  `cl_contact_email` varchar(30) DEFAULT NULL,
  `tm_contact` varchar(30) DEFAULT NULL,
  `tm_contact_email` varchar(30) DEFAULT NULL,
  `cl_modify_date` datetime DEFAULT NULL,
  PRIMARY KEY (`cl_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sp_collection`
--

DROP TABLE IF EXISTS `sp_collection`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sp_collection` (
  `coll_id` int NOT NULL AUTO_INCREMENT,
  `coll_name` varchar(30) NOT NULL,
  `coll_shortname` varchar(15) NOT NULL,
  `coll_date` datetime NOT NULL,
  `is_active_fg` tinyint NOT NULL,
  `coll_dir_location` varchar(255) DEFAULT NULL,
  `coll_collected_by` varchar(30) DEFAULT NULL,
  `coll_collector_email` varchar(255) DEFAULT NULL,
  `coll_objective` varchar(255) DEFAULT NULL,
  `sp_project_pr_id` int NOT NULL,
  PRIMARY KEY (`coll_id`),
  KEY `sp_project_pr_id` (`sp_project_pr_id`),
  CONSTRAINT `sp_collection_ibfk_1` FOREIGN KEY (`sp_project_pr_id`) REFERENCES `sp_project` (`pr_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sp_database`
--

DROP TABLE IF EXISTS `sp_database`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sp_database` (
  `db_id` int NOT NULL AUTO_INCREMENT,
  `db_name` varchar(30) NOT NULL,
  `db_shortname` varchar(15) NOT NULL,
  `db_filename` varchar(255) DEFAULT NULL,
  `db_fileread_date` datetime DEFAULT NULL,
  `db_collection_host` varchar(30) DEFAULT NULL,
  `is_cluster_fg` tinyint DEFAULT NULL,
  `is_active_fg` tinyint DEFAULT NULL,
  `sp_collection_coll_id` int NOT NULL,
  `db_host_cpu` varchar(75) DEFAULT NULL,
  `db_host_model` varchar(30) DEFAULT NULL,
  `sp_host_hs_id` int DEFAULT NULL,
  PRIMARY KEY (`db_id`),
  KEY `sp_collection_coll_id` (`sp_collection_coll_id`),
  CONSTRAINT `sp_database_ibfk_1` FOREIGN KEY (`sp_collection_coll_id`) REFERENCES `sp_collection` (`coll_id`)
) ENGINE=InnoDB AUTO_INCREMENT=400 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sp_dbidentity`
--

DROP TABLE IF EXISTS `sp_dbidentity`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sp_dbidentity` (
  `iden_id` int NOT NULL AUTO_INCREMENT,
  `iden_metric` varchar(30) DEFAULT NULL,
  `iden_acronym` varchar(30) DEFAULT NULL,
  `iden_instance` int DEFAULT NULL,
  `iden_metricdate` datetime DEFAULT NULL,
  `iden_metricvalue` varchar(75) DEFAULT NULL,
  `sp_database_db_id` int NOT NULL,
  PRIMARY KEY (`iden_id`),
  KEY `sp_database_db_id` (`sp_database_db_id`),
  CONSTRAINT `sp_dbidentity_ibfk_1` FOREIGN KEY (`sp_database_db_id`) REFERENCES `sp_database` (`db_id`)
) ENGINE=InnoDB AUTO_INCREMENT=6282 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sp_dbmetric`
--

DROP TABLE IF EXISTS `sp_dbmetric`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sp_dbmetric` (
  `metr_id` int NOT NULL AUTO_INCREMENT,
  `metr_metric` varchar(30) DEFAULT NULL,
  `metr_acronym` varchar(30) DEFAULT NULL,
  `metr_instance` int DEFAULT NULL,
  `metr_metricdate` datetime DEFAULT NULL,
  `metr_metricvalue` varchar(75) DEFAULT NULL,
  `sp_database_db_id` int NOT NULL,
  PRIMARY KEY (`metr_id`),
  KEY `sp_database_db_id` (`sp_database_db_id`),
  CONSTRAINT `sp_dbmetric_ibfk_1` FOREIGN KEY (`sp_database_db_id`) REFERENCES `sp_database` (`db_id`)
) ENGINE=InnoDB AUTO_INCREMENT=54955562 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sp_dbmetric_summ`
--

DROP TABLE IF EXISTS `sp_dbmetric_summ`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sp_dbmetric_summ` (
  `ms_id` int NOT NULL AUTO_INCREMENT,
  `ms_metric` varchar(30) NOT NULL,
  `ms_acronym` varchar(30) NOT NULL,
  `ms_instance` int DEFAULT NULL,
  `ms_avgvalue` varchar(30) DEFAULT NULL,
  `ms_maxvalue` varchar(30) DEFAULT NULL,
  `sp_database_db_id` int DEFAULT NULL,
  PRIMARY KEY (`ms_id`),
  KEY `sp_database_db_id` (`sp_database_db_id`),
  CONSTRAINT `sp_dbmetric_summ_ibfk_1` FOREIGN KEY (`sp_database_db_id`) REFERENCES `sp_database` (`db_id`)
) ENGINE=InnoDB AUTO_INCREMENT=10149 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sp_ExaFrame`
--

DROP TABLE IF EXISTS `sp_ExaFrame`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sp_ExaFrame` (
  `fr_id` int NOT NULL AUTO_INCREMENT,
  `fr_name` varchar(30) NOT NULL,
  `fr_location` varchar(30) NOT NULL,
  `fr_model` varchar(30) DEFAULT NULL,
  `is_active_fg` tinyint DEFAULT NULL,
  PRIMARY KEY (`fr_id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sp_host`
--

DROP TABLE IF EXISTS `sp_host`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sp_host` (
  `hs_id` int NOT NULL AUTO_INCREMENT,
  `hs_name` varchar(30) NOT NULL,
  `hs_location` varchar(30) NOT NULL,
  `hs_instance` int DEFAULT NULL,
  `is_active_fg` tinyint DEFAULT NULL,
  `sp_exaframe_fr_id` int DEFAULT NULL,
  PRIMARY KEY (`hs_id`),
  KEY `sp_exaframe_fr_id` (`sp_exaframe_fr_id`),
  CONSTRAINT `sp_host_ibfk_1` FOREIGN KEY (`sp_exaframe_fr_id`) REFERENCES `sp_exaframe` (`fr_id`)
) ENGINE=InnoDB AUTO_INCREMENT=51 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sp_MetricPlot`
--

DROP TABLE IF EXISTS `sp_MetricPlot`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sp_MetricPlot` (
  `mp_id` int NOT NULL AUTO_INCREMENT,
  `mp_metricName` varchar(30) NOT NULL,
  `mp_metricAcronym` varchar(30) NOT NULL,
  `mp_instance` int DEFAULT NULL,
  `mp_plotdate` datetime DEFAULT NULL,
  `mp_plotvalue` varchar(75) DEFAULT NULL,
  `sp_database_db_id` int NOT NULL,
  PRIMARY KEY (`mp_id`),
  KEY `sp_database_db_id` (`sp_database_db_id`),
  CONSTRAINT `sp_metricplot_ibfk_1` FOREIGN KEY (`sp_database_db_id`) REFERENCES `sp_database` (`db_id`)
) ENGINE=InnoDB AUTO_INCREMENT=45099861 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sp_project`
--

DROP TABLE IF EXISTS `sp_project`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sp_project` (
  `pr_id` int NOT NULL AUTO_INCREMENT,
  `pr_name` varchar(30) NOT NULL,
  `pr_shortname` varchar(15) NOT NULL,
  `pr_creation_date` datetime NOT NULL,
  `is_active_fg` tinyint DEFAULT NULL,
  `pr_modify_date` datetime DEFAULT NULL,
  `sp_client_cl_id` int NOT NULL,
  PRIMARY KEY (`pr_id`),
  KEY `sp_client_cl_id` (`sp_client_cl_id`),
  CONSTRAINT `sp_project_ibfk_1` FOREIGN KEY (`sp_client_cl_id`) REFERENCES `sp_client` (`cl_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sp_user`
--

DROP TABLE IF EXISTS `sp_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sp_user` (
  `us_id` int NOT NULL AUTO_INCREMENT,
  `us_username` varchar(15) NOT NULL,
  `us_password` varchar(15) NOT NULL,
  `us_first_name` varchar(15) DEFAULT NULL,
  `us_last_name` varchar(15) NOT NULL,
  `is_su_fg` tinyint DEFAULT NULL,
  `is_active_fg` tinyint NOT NULL,
  `us_organization` varchar(15) DEFAULT NULL,
  `us_email` varchar(75) DEFAULT NULL,
  PRIMARY KEY (`us_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_client_xref`
--

DROP TABLE IF EXISTS `user_client_xref`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_client_xref` (
  `uc_us_id` int NOT NULL,
  `uc_cl_id` int NOT NULL,
  `is_active_fg` tinyint NOT NULL,
  `sp_user_us_id` int NOT NULL,
  `sp_client_cl_id` int NOT NULL,
  PRIMARY KEY (`uc_us_id`,`uc_cl_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

