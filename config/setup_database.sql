-- Create database.
CREATE SCHEMA `jukeboxdb` ;

-- Create `parties` table.
CREATE TABLE `jukeboxdb`.`parties` (
  `unique_id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id` VARCHAR(64) NULL,
  `user_spotify_token` VARCHAR(1024) NULL;
  `party_id` VARCHAR(64) NULL,
  `time_created` VARCHAR(64) NULL,
  PRIMARY KEY (`unique_id`),
  UNIQUE INDEX `row_id_UNIQUE` (`unique_id` ASC));