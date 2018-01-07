CREATE TABLE IF NOT EXISTS `news_item` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` text,
  `link` text,
  `fetch_date` datetime DEFAULT NULL,
  `pub_date` datetime DEFAULT NULL,
  `description` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
