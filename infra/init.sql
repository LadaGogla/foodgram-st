GRANT ALL PRIVILEGES ON DATABASE foodgram TO foodgram_user; 

-- Изменение сортировки для поля name в таблице ингредиентов
ALTER TABLE recipes_ingredient ALTER COLUMN name TYPE VARCHAR(200) COLLATE "C";

-- Изменение сортировки для поля name в таблице рецептов
ALTER TABLE recipes_recipe ALTER COLUMN name TYPE VARCHAR(200) COLLATE "C"; 