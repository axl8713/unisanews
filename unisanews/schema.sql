CREATE TABLE IF NOT EXISTS `news_item` (
  `id` INTEGER PRIMARY KEY,
  `title` text,
  `link` text,
  `fetch_date` timestamp DEFAULT NULL,
  `pub_date` timestamp DEFAULT NULL,
  `description` text
);
