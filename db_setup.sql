create table emails (
	email VARCHAR(255)
);

create table external (
	website VARCHAR(255)
);

create table firm (
	details TEXT,
    site VARCHAR(255)
);

GRANT ALL PRIVILEGES ON cpa.*
	TO 'python'@'localhost'
	IDENTIFIED BY 'python';
    
Error Code: 1044. Access denied for user 'chris'@'localhost' to database 'cpa'
