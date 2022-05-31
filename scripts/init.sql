create database edu default character set utf8mb4 collate utf8mb4_unicode_ci;
use edu;
SET NAMES utf8;
SET FOREIGN_KEY_CHECKS = 0;
-- ----------------------------
--  Table structure for `category`
-- ----------------------------
DROP TABLE IF EXISTS `category`;
CREATE TABLE `category` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `create_time` datetime NOT NULL,
  `update_time` datetime NOT NULL,
  `name` varchar(191) COLLATE utf8mb4_unicode_ci NOT NULL,
  `pid` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `category_name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
--  Records of `category`
-- ----------------------------
BEGIN;
INSERT INTO `category` VALUES ('1', '2022-05-10 12:41:11', '2022-05-10 12:41:11', 'Python', '0'), ('2', '2022-05-10 12:41:11', '2022-05-10 12:41:11', 'Java', '0'), ('3', '2022-05-10 12:41:11', '2022-05-10 12:41:11', 'Go lang', '0'), ('4', '2022-05-10 12:41:11', '2022-05-10 12:41:11', 'Tornado', '1'), ('5', '2022-05-10 12:41:11', '2022-05-10 12:41:11', 'Django', '2'), ('6', '2022-05-10 12:41:11', '2022-05-10 12:41:11', 'template', '5');
COMMIT;

-- ----------------------------
--  Table structure for `course`
-- ----------------------------
DROP TABLE IF EXISTS `course`;
CREATE TABLE `course` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `create_time` datetime NOT NULL,
  `update_time` datetime NOT NULL,
  `title` varchar(191) COLLATE utf8mb4_unicode_ci NOT NULL,
  `desc` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `cid_id` bigint(20) NOT NULL,
  `price` bigint(20) NOT NULL,
  `thumb` varchar(191) COLLATE utf8mb4_unicode_ci NOT NULL,
  `video` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `vtype` int(11) NOT NULL,
  `uid_id` bigint(20) NOT NULL,
  `audit` int(11) NOT NULL,
  `state` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `course_title` (`title`),
  KEY `course_cid_id` (`cid_id`),
  KEY `course_uid_id` (`uid_id`),
  CONSTRAINT `course_ibfk_1` FOREIGN KEY (`cid_id`) REFERENCES `category` (`id`),
  CONSTRAINT `course_ibfk_2` FOREIGN KEY (`uid_id`) REFERENCES `category` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
--  Records of `course`
-- ----------------------------
BEGIN;
INSERT INTO `course` VALUES ('1', '2022-05-11 16:51:58', '2022-05-19 09:24:17', 'Combining Data in Pandas With merge(), .join(), and concat()', 'Combining Data in Pandas With merge(), .join(), and concat()', '1', '10', 'Build-a-Project-With-FastAPI_Watermarked.cb19f6b7b108.jpeg', '<iframe src=\"https://player.bilibili.com/player.html?aid=251955199&bvid=BV13Y411s79j&cid=447815214&page=1\" allowfullscreen=\"allowfullscreen\" width=\"100%\" height=\"500\" scrolling=\"no\" frameborder=\"0\" sandbox=\"allow-top-navigation allow-same-origin allow-forms allow-scripts\"></iframe>', '2', '5', '5', '1'), ('2', '2022-05-11 16:55:19', '2022-05-19 09:24:19', 'Python News: What\'s New From April 2022', 'Python News: What\'s New From April 2022', '1', '0', 'A-Guide-to-Python-Keywords_Watermarked.73f8f57a93ed.jpeg', '<iframe src=\"https://player.bilibili.com/player.html?aid=251955199&bvid=BV13Y411s79j&cid=447815214&page=1\" allowfullscreen=\"allowfullscreen\" width=\"100%\" height=\"500\" scrolling=\"no\" frameborder=\"0\" sandbox=\"allow-top-navigation allow-same-origin allow-forms allow-scripts\"></iframe>', '2', '5', '5', '1'), ('3', '2022-05-11 16:55:57', '2022-05-19 18:05:55', 'Sorting Data in Python With Pandas', 'Sorting Data in Python With Pandas', '4', '0', 'Build-a-Site-Connectivity-Checker_Watermarked.4e66b0f9cc0b.jpeg', '<iframe src=\"https://player.bilibili.com/player.html?aid=251955199&bvid=BV13Y411s79j&cid=447815214&page=1\" allowfullscreen=\"allowfullscreen\" width=\"100%\" height=\"500\" scrolling=\"no\" frameborder=\"0\" sandbox=\"allow-top-navigation allow-same-origin allow-forms allow-scripts\"></iframe>', '2', '5', '5', '1');
COMMIT;


-- ----------------------------
--  Table structure for `role`
-- ----------------------------
DROP TABLE IF EXISTS `role`;
CREATE TABLE `role` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `create_time` datetime NOT NULL,
  `update_time` datetime NOT NULL,
  `role_name` varchar(191) COLLATE utf8mb4_unicode_ci NOT NULL,
  `auth` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `role_role_name` (`role_name`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
--  Records of `role`
-- ----------------------------
BEGIN;
INSERT INTO `role` VALUES ('1', '2022-05-09 09:34:38', '2022-05-09 09:34:38', '老师', '0'), ('3', '2022-05-09 09:35:35', '2022-05-09 09:35:35', '学生', '0'), ('4', '2022-05-09 09:35:35', '2022-05-09 09:35:35', '后台管理', '15'), ('5', '2022-05-09 09:35:35', '2022-05-09 09:35:35', '客服', '0');
COMMIT;

-- ----------------------------
--  Table structure for `user`
-- ----------------------------
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `create_time` datetime NOT NULL,
  `update_time` datetime NOT NULL,
  `email` varchar(191) COLLATE utf8mb4_unicode_ci NOT NULL,
  `password` varchar(191) COLLATE utf8mb4_unicode_ci NOT NULL,
  `role_id` bigint(20) NOT NULL,
  `state` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_email` (`email`),
  KEY `user_role_id` (`role_id`),
  CONSTRAINT `user_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `role` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
--  Records of `user`
-- ----------------------------
BEGIN;
INSERT INTO `user` VALUES ('1', '2022-05-09 09:53:48', '2022-05-09 09:53:48', '123', 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', '1', '0'), ('4', '2022-05-09 11:11:06', '2022-05-09 11:11:06', '333', '556d7dc3a115356350f1f9910b1af1ab0e312d4b3e4fc788d2da63668f36d017', '1', '0'), ('5', '2022-05-09 12:07:15', '2022-05-09 12:07:15', 'zcxey2911@hotmail.com', 'b1e99324505bd32da0e1f85dcf5e19a09db0481e8a15f62c41eb320304a8e927', '3', '0');
COMMIT;

SET FOREIGN_KEY_CHECKS = 1;


-- ----------------------------
--  Table structure for `order`
-- ----------------------------
DROP TABLE IF EXISTS `order`;
CREATE TABLE `order` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `create_time` datetime NOT NULL,
  `update_time` datetime NOT NULL,
  `orderid` varchar(191) COLLATE utf8mb4_unicode_ci NOT NULL,
  `price` bigint(20) NOT NULL,
  `uid_id` bigint(20) NOT NULL,
  `cid_id` bigint(20) NOT NULL,
  `channel` int(11) NOT NULL,
  `state` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `order_uid_id` (`uid_id`),
  KEY `order_cid_id` (`cid_id`),
  CONSTRAINT `order_ibfk_1` FOREIGN KEY (`uid_id`) REFERENCES `user` (`id`),
  CONSTRAINT `order_ibfk_2` FOREIGN KEY (`cid_id`) REFERENCES `course` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ----------------------------
--  Records of `order`
-- ----------------------------
BEGIN;
INSERT INTO `order` VALUES ('4', '2022-05-17 19:51:40', '2022-05-18 09:30:33', '20220517195139941997148548352931', '10', '5', '1', '1', '3'), ('5', '2022-05-17 19:58:24', '2022-05-17 19:58:24', '20220517195823843280183792469033', '10', '5', '1', '1', '0'), ('6', '2022-05-23 20:34:07', '2022-05-23 20:34:07', '20220523203407056862114905295246', '0', '5', '2', '1', '0');
COMMIT;
