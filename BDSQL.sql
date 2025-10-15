CREATE DATABASE IF NOT EXISTS `blockvaultapi`;
USE `blockvaultapi`;

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

DELIMITER //
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
//
DELIMITER ;

DELIMITER //
CREATE FUNCTION `file_exists` (
  `p_file_name` VARCHAR(255)
) RETURNS TINYINT(1)
DETERMINISTIC
BEGIN
  DECLARE v_exists TINYINT(1);
  SELECT EXISTS (SELECT 1 FROM records WHERE file_name = p_file_name) INTO v_exists;
  RETURN v_exists;
END;
//
DELIMITER ;

DELIMITER //
CREATE PROCEDURE `file_id` (
    IN p_file_name VARCHAR(255),
    OUT p_idfile INT,
    OUT p_message VARCHAR(255)
)
BEGIN
    IF file_exists(p_file_name) = 1 THEN
        SELECT id_file INTO p_idfile
        FROM records
        WHERE file_name = p_file_name
        LIMIT 1;
        SET p_message = 'Archivo encontrado';
    ELSE
        SET p_idfile = NULL;
        SET p_message = 'Archivo no encontrado';
    END IF;
END;
//
DELIMITER ;
