/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19  Distrib 10.5.29-MariaDB, for debian-linux-gnu (aarch64)
--
-- Host: localhost    Database: Parqueadero1
-- ------------------------------------------------------
-- Server version	10.5.29-MariaDB-0+deb11u1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `Cambios`
--

DROP TABLE IF EXISTS `Cambios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `Cambios` (
  `id` int(20) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(255) NOT NULL,
  `valor_anterior` varchar(255) NOT NULL,
  `valor_nuevo` varchar(255) NOT NULL,
  `tipo_cambio` varchar(255) NOT NULL,
  `hora` datetime NOT NULL,
  `nombre_usuario` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=199 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Cortes`
--

DROP TABLE IF EXISTS `Cortes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `Cortes` (
  `Folio` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `FechaIni` datetime NOT NULL,
  `FechaFin` datetime NOT NULL,
  `Importe` int(11) DEFAULT NULL,
  `NumBoletos` int(11) DEFAULT NULL,
  `TipoDCorte` smallint(6) DEFAULT NULL,
  `Quedados` int(11) DEFAULT NULL,
  `idInicial` int(11) DEFAULT NULL,
  `NumBolQued` int(11) DEFAULT NULL,
  `Pensionados_Quedados` int(10) DEFAULT NULL,
  PRIMARY KEY (`Folio`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Entradas`
--

DROP TABLE IF EXISTS `Entradas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `Entradas` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `Entrada` datetime NOT NULL,
  `Salida` datetime DEFAULT NULL,
  `TiempoTotal` varchar(255) DEFAULT NULL,
  `Importe` float DEFAULT NULL,
  `CorteInc` int(11) DEFAULT NULL,
  `vobo` varchar(5) DEFAULT NULL,
  `Placas` varchar(255) DEFAULT NULL,
  `TarifaPreferente` varchar(255) DEFAULT NULL,
  `TipoPromocion` varchar(255) DEFAULT NULL,
  `QRpromo` varchar(25) DEFAULT NULL,
  `Motivo` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Recobros`
--

DROP TABLE IF EXISTS `Recobros`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `Recobros` (
  `Id_recobro` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `Id_entrada` bigint(20) unsigned NOT NULL,
  `Fecha_pago` datetime NOT NULL,
  `Minutos_excedidos` int(11) NOT NULL,
  `Importe` float NOT NULL,
  `CorteInc` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`Id_recobro`),
  KEY `Id_entrada` (`Id_entrada`),
  CONSTRAINT `Recobros_ibfk_1` FOREIGN KEY (`Id_entrada`) REFERENCES `Entradas` (`id`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `MovimientosPens`
--

DROP TABLE IF EXISTS `MovimientosPens`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `MovimientosPens` (
  `Id_movs` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `Idcliente` int(10) unsigned NOT NULL,
  `num_tarjeta` int(11) NOT NULL,
  `Entrada` datetime DEFAULT NULL,
  `Salida` datetime DEFAULT NULL,
  `TiempoTotal` varchar(255) DEFAULT NULL,
  `Estatus` varchar(15) DEFAULT NULL,
  `Corte` int(10) DEFAULT NULL,
  PRIMARY KEY (`Id_movs`),
  KEY `Idcliente` (`Idcliente`),
  CONSTRAINT `MovimientosPens_ibfk_1` FOREIGN KEY (`Idcliente`) REFERENCES `Pensionados` (`Id_cliente`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `MovsUsuarios`
--

DROP TABLE IF EXISTS `MovsUsuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `MovsUsuarios` (
  `Id_movs` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `Idusuario` int(10) unsigned NOT NULL,
  `usuario` varchar(25) NOT NULL,
  `inicio` datetime DEFAULT NULL,
  `nombre` varchar(255) DEFAULT NULL,
  `turno` int(11) DEFAULT NULL,
  `comentarios` varchar(255) DEFAULT NULL,
  `CierreCorte` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`Id_movs`),
  KEY `Idusuario` (`Idusuario`),
  CONSTRAINT `MovsUsuarios_ibfk_1` FOREIGN KEY (`Idusuario`) REFERENCES `Usuarios` (`Id_usuario`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `PagosPens`
--

DROP TABLE IF EXISTS `PagosPens`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `PagosPens` (
  `Id_pago` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `Idcliente` int(10) unsigned NOT NULL,
  `num_tarjeta` int(11) NOT NULL,
  `Fecha_pago` datetime DEFAULT NULL,
  `Fecha_vigencia` datetime DEFAULT NULL,
  `Mensualidad` varchar(255) DEFAULT NULL,
  `Monto` float DEFAULT NULL,
  `TipoPago` enum('Transferencia','Efectivo') NOT NULL,
  PRIMARY KEY (`Id_pago`),
  KEY `Idcliente` (`Idcliente`),
  CONSTRAINT `PagosPens_ibfk_1` FOREIGN KEY (`Idcliente`) REFERENCES `Pensionados` (`Id_cliente`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Pensionados`
--

DROP TABLE IF EXISTS `Pensionados`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `Pensionados` (
  `Id_cliente` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `Num_tarjeta` int(11) NOT NULL,
  `Nom_cliente` varchar(255) DEFAULT NULL,
  `Apell1_cliente` varchar(255) DEFAULT NULL,
  `Apell2_cliente` varchar(255) DEFAULT NULL,
  `Fecha_alta` datetime DEFAULT NULL,
  `Telefono1` varchar(25) DEFAULT NULL,
  `Telefono2` varchar(25) DEFAULT NULL,
  `Ciudad` varchar(255) DEFAULT NULL,
  `Colonia` varchar(255) DEFAULT NULL,
  `CP` varchar(8) DEFAULT NULL,
  `Calle_num` varchar(255) DEFAULT NULL,
  `Placas` varchar(50) DEFAULT NULL,
  `Modelo_auto` varchar(50) DEFAULT NULL,
  `Color_auto` varchar(20) DEFAULT NULL,
  `Vigencia` varchar(20) DEFAULT NULL,
  `Fecha_vigencia` datetime DEFAULT NULL,
  `Monto` int(15) DEFAULT NULL,
  `Estatus` varchar(20) DEFAULT NULL,
  `Tolerancia` varchar(20) DEFAULT NULL,
  `Cortesia` varchar(20) DEFAULT NULL,
  `Ult_Cambio` datetime DEFAULT NULL,
  PRIMARY KEY (`Id_cliente`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Usuarios`
--

DROP TABLE IF EXISTS `Usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `Usuarios` (
  `Id_usuario` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `Usuario` varchar(25) NOT NULL,
  `Contrasena` varchar(25) DEFAULT NULL,
  `Nom_usuario` varchar(255) DEFAULT NULL,
  `Fecha_alta` datetime DEFAULT NULL,
  `Telefono1` varchar(25) DEFAULT NULL,
  `Aviso_Emer` varchar(255) DEFAULT NULL,
  `TelefonoEmer` varchar(25) DEFAULT NULL,
  `Sucursal` varchar(25) DEFAULT NULL,
  PRIMARY KEY (`Id_usuario`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping events for database 'Parqueadero1'
--

--
-- Dumping routines for database 'Parqueadero1'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-08-25 16:21:19
