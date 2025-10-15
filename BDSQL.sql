CREATE DATABASE IF NOT EXISTS `blockvaultapi`;
USE `sistema_usuario`;

CREATE TABLE IF NOT EXISTS `records` (
  `records_id` INT UNSIGNED ZEROFILL AUTO_INCREMENT NOT NULL,
  `hash_block` CHAR(64) NOT NULL,
  `hash_file` CHAR(64) NOT NULL,
  `id_file` INT NOT NULL,
  `id_block` INT NOT NULL,
  `file_name` VARCHAR(255) NOT NULL,
  `data` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
   PRIMARY KEY (`records_id`)
);

CREATE PROCEDURE `save_data` (
  IN `p_hash_block` CHAR(64),
  IN `p_hash_file` CHAR(64),
  IN `p_id_file` INT,
  IN `p_id_block` INT,
  IN `p_file_name` VARCHAR(255)
)
BEGIN
  INSERT INTO records (hash_block, hash_file, id_file, id_block, file_name)
  VALUES (p_hash_block, p_hash_file, p_id_file, p_id_block, p_file_name);
END;


