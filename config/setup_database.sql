-- Create database.
CREATE SCHEMA `jukeboxdb` ;

-- Create `parties` table.
CREATE TABLE `jukeboxdb`.`parties` (
  `unique_id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `party_id` VARCHAR(256) NULL,
  `user_id` VARCHAR(256) NULL,
  `party_name` VARCHAR(1024) NULL,
  `party_description` VARCHAR(1024) NULL,
  `party_starter_playlist` VARCHAR(256) NULL,
  `party_exported_playlist` VARCHAR(256) NULL,
  `time_created` VARCHAR(256) NULL,
  PRIMARY KEY (`unique_id`),
  UNIQUE INDEX `row_id_UNIQUE` (`unique_id` ASC));