server/port: murcnvepachedu/3306
schema: biometrics
user/pwd: biometric-user/B10M37R1K5

tables -> STREAM_IMG, TRAIN_IMG

==============

create database biometrics;
CREATE USER `biometric-user`@`%` IDENTIFIED BY 'B10M37R1K5';
use biometrics
GRANT ALL PRIVILEGES ON biometrics TO `biometric-user`@`%` WITH GRANT OPTION;



CREATE TABLE `biometrics`.`stream_img` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `EMP_ID` varchar(45) DEFAULT NULL,
  `LAN_ID` varchar(45) NOT NULL,
  `CAPTURE_TIME` datetime NOT NULL,
  `IMAGE` blob,
  `PROCESSED_TIME` datetime DEFAULT NULL,
  `STATUS` varchar(45) DEFAULT NULL,
  `RESULT` varchar(45) DEFAULT NULL,
  `ACCURACY` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`ID`,`LAN_ID`,`CAPTURE_TIME`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;


CREATE TABLE `biometrics`.`train_img` (
  `ID` int(11) NOT NULL,
  `EMP_ID` varchar(45) DEFAULT NULL,
  `LAN_ID` varchar(45) NOT NULL,
  `CAPTURE_TIME` datetime NOT NULL,
  `IMAGE` blob,
  `PROCESSED_TIME` datetime DEFAULT NULL,
  `STATUS` varchar(45) DEFAULT NULL,
  `RESULT` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`ID`,`LAN_ID`,`CAPTURE_TIME`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
