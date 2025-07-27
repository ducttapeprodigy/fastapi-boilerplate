-- IPAM Abstraction Platform Database Schema
-- SQL Server Implementation

-- Create database (uncomment if creating new database)
-- CREATE DATABASE IPAMAbstraction;
-- USE IPAMAbstraction;

-- ==================================================
-- CORE ENTITY TABLES
-- ==================================================

-- Locations Table (flat structure from underlying systems)
CREATE TABLE locations (
    location_id INT IDENTITY(1,1) PRIMARY KEY,
    location_code NVARCHAR(50) NOT NULL UNIQUE,
    location_name NVARCHAR(255) NULL,
    created_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    updated_at DATETIME2 NOT NULL DEFAULT GETDATE()
);

-- Blocks Table (highest level network containers)
CREATE TABLE blocks (
    block_id INT IDENTITY(1,1) PRIMARY KEY,
    object_id NVARCHAR(255) NOT NULL UNIQUE,
    config_path NVARCHAR(500) NOT NULL,
    cidr NVARCHAR(50) NOT NULL,
    name NVARCHAR(255) NULL,
    description NVARCHAR(1000) NULL,
    location_id INT NOT NULL,
    created_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    updated_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    FOREIGN KEY (location_id) REFERENCES locations(location_id)
);

-- Networks Table (contained within blocks)
CREATE TABLE networks (
    network_id INT IDENTITY(1,1) PRIMARY KEY,
    object_id NVARCHAR(255) NOT NULL UNIQUE,
    config_path NVARCHAR(500) NOT NULL,
    cidr NVARCHAR(50) NOT NULL,
    vlan_id INT NULL,
    name NVARCHAR(255) NULL,
    description NVARCHAR(1000) NULL,
    block_id INT NOT NULL,
    created_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    updated_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    FOREIGN KEY (block_id) REFERENCES blocks(block_id)
);

-- Hosts Table (contained within networks)
CREATE TABLE hosts (
    host_id INT IDENTITY(1,1) PRIMARY KEY,
    object_id NVARCHAR(255) NOT NULL UNIQUE,
    config_path NVARCHAR(500) NOT NULL,
    name NVARCHAR(255) NULL,
    description NVARCHAR(1000) NULL,
    status NVARCHAR(50) NOT NULL CHECK (status IN ('active', 'pending_change', 'deleted')),
    pending_change NVARCHAR(1000) NULL,
    network_id INT NOT NULL,
    created_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    updated_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    FOREIGN KEY (network_id) REFERENCES networks(network_id)
);

-- ==================================================
-- TAGGING SYSTEM TABLES
-- ==================================================

-- Tag Groups Table (logical collections of similar tags)
CREATE TABLE tag_groups (
    tag_group_id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(100) NOT NULL UNIQUE,
    created_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    updated_at DATETIME2 NOT NULL DEFAULT GETDATE()
);

-- Tags Table (individual tags belonging to groups)
CREATE TABLE tags (
    tag_id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(100) NOT NULL,
    tag_group_id INT NOT NULL,
    created_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    updated_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    FOREIGN KEY (tag_group_id) REFERENCES tag_groups(tag_group_id),
    UNIQUE (name, tag_group_id) -- Tag names must be unique within a group
);

-- ==================================================
-- MANY-TO-MANY JUNCTION TABLES FOR TAGGING
-- ==================================================

-- Block Tags Junction Table
CREATE TABLE block_tags (
    block_id INT NOT NULL,
    tag_id INT NOT NULL,
    created_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    PRIMARY KEY (block_id, tag_id),
    FOREIGN KEY (block_id) REFERENCES blocks(block_id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(tag_id) ON DELETE CASCADE
);

-- Network Tags Junction Table
CREATE TABLE network_tags (
    network_id INT NOT NULL,
    tag_id INT NOT NULL,
    created_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    PRIMARY KEY (network_id, tag_id),
    FOREIGN KEY (network_id) REFERENCES networks(network_id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(tag_id) ON DELETE CASCADE
);

-- Host Tags Junction Table
CREATE TABLE host_tags (
    host_id INT NOT NULL,
    tag_id INT NOT NULL,
    created_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    PRIMARY KEY (host_id, tag_id),
    FOREIGN KEY (host_id) REFERENCES hosts(host_id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(tag_id) ON DELETE CASCADE
);

-- ==================================================
-- CONFIGURATION TABLE
-- ==================================================

-- Application Configuration Table
CREATE TABLE app_configuration (
    config_id INT IDENTITY(1,1) PRIMARY KEY,
    config_key NVARCHAR(255) NOT NULL UNIQUE,
    config_value NVARCHAR(MAX) NULL, -- Supports JSON, arrays, complex data types
    category NVARCHAR(100) NULL,
    description NVARCHAR(500) NULL,
    created_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    updated_at DATETIME2 NOT NULL DEFAULT GETDATE()
);

-- ==================================================
-- INDEXES FOR PERFORMANCE
-- ==================================================

-- Index on foreign key relationships
CREATE INDEX IX_blocks_location_id ON blocks(location_id);
CREATE INDEX IX_networks_block_id ON networks(block_id);
CREATE INDEX IX_hosts_network_id ON hosts(network_id);
CREATE INDEX IX_tags_tag_group_id ON tags(tag_group_id);

-- Index on frequently queried fields
CREATE INDEX IX_blocks_config_path ON blocks(config_path);
CREATE INDEX IX_networks_config_path ON networks(config_path);
CREATE INDEX IX_hosts_config_path ON hosts(config_path);
CREATE INDEX IX_hosts_status ON hosts(status);
CREATE INDEX IX_app_configuration_category ON app_configuration(category);

-- Index on CIDR fields for network queries
CREATE INDEX IX_blocks_cidr ON blocks(cidr);
CREATE INDEX IX_networks_cidr ON networks(cidr);

-- ==================================================
-- TRIGGERS FOR AUTOMATIC TIMESTAMP UPDATES
-- ==================================================

-- Update timestamp trigger for locations
CREATE TRIGGER tr_locations_updated_at
ON locations
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE locations 
    SET updated_at = GETDATE()
    FROM locations l
    INNER JOIN inserted i ON l.location_id = i.location_id;
END;

-- Update timestamp trigger for blocks
CREATE TRIGGER tr_blocks_updated_at
ON blocks
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE blocks 
    SET updated_at = GETDATE()
    FROM blocks b
    INNER JOIN inserted i ON b.block_id = i.block_id;
END;

-- Update timestamp trigger for networks
CREATE TRIGGER tr_networks_updated_at
ON networks
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE networks 
    SET updated_at = GETDATE()
    FROM networks n
    INNER JOIN inserted i ON n.network_id = i.network_id;
END;

-- Update timestamp trigger for hosts
CREATE TRIGGER tr_hosts_updated_at
ON hosts
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE hosts 
    SET updated_at = GETDATE()
    FROM hosts h
    INNER JOIN inserted i ON h.host_id = i.host_id;
END;

-- Update timestamp trigger for tag_groups
CREATE TRIGGER tr_tag_groups_updated_at
ON tag_groups
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE tag_groups 
    SET updated_at = GETDATE()
    FROM tag_groups tg
    INNER JOIN inserted i ON tg.tag_group_id = i.tag_group_id;
END;

-- Update timestamp trigger for tags
CREATE TRIGGER tr_tags_updated_at
ON tags
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE tags 
    SET updated_at = GETDATE()
    FROM tags t
    INNER JOIN inserted i ON t.tag_id = i.tag_id;
END;

-- Update timestamp trigger for app_configuration
CREATE TRIGGER tr_app_configuration_updated_at
ON app_configuration
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE app_configuration 
    SET updated_at = GETDATE()
    FROM app_configuration ac
    INNER JOIN inserted i ON ac.config_id = i.config_id;
END;

-- ==================================================
-- SAMPLE DATA INSERTION (Optional)
-- ==================================================

-- Sample locations
INSERT INTO locations (location_code, location_name) VALUES
('NYC-DC1', 'New York Data Center 1'),
('LAX-DC1', 'Los Angeles Data Center 1'),
('CHI-DC1', 'Chicago Data Center 1');

-- Sample tag groups
INSERT INTO tag_groups (name) VALUES
('Security Zones'),
('Environment'),
('Function'),
('Compliance');

-- Sample tags
INSERT INTO tags (name, tag_group_id) VALUES
('DMZ', 1),
('Internal', 1),
('External', 1),
('Production', 2),
('Staging', 2),
('Development', 2),
('Web Server', 3),
('Database', 3),
('Load Balancer', 3),
('PCI Compliant', 4),
('HIPAA Compliant', 4);

-- Sample configuration entries
INSERT INTO app_configuration (config_key, config_value, category, description) VALUES
('ipam.sync.interval', '300', 'sync', 'Sync interval in seconds for IPAM data refresh'),
('ui.default.page.size', '50', 'ui', 'Default number of items per page in UI lists'),
('security.zones.inherit', 'true', 'security', 'Whether security zone tags inherit to child objects'),
('notification.email.enabled', 'true', 'notifications', 'Enable email notifications for system events'),
('api.rate.limit.requests', '1000', 'api', 'Maximum API requests per hour per client'),
('ui.theme.options', '["light", "dark", "auto"]', 'ui', 'Available theme options for the UI');

-- ==================================================
-- VIEWS FOR COMMON QUERIES (Optional)
-- ==================================================

-- View for hosts with inherited tags from parent network and block
CREATE VIEW vw_hosts_with_inherited_tags AS
SELECT 
    h.host_id,
    h.object_id,
    h.name AS host_name,
    h.status,
    n.name AS network_name,
    n.cidr AS network_cidr,
    b.name AS block_name,
    b.cidr AS block_cidr,
    l.location_name,
    t.name AS tag_name,
    tg.name AS tag_group_name,
    'host' AS tag_source
FROM hosts h
JOIN networks n ON h.network_id = n.network_id
JOIN blocks b ON n.block_id = b.block_id
JOIN locations l ON b.location_id = l.location_id
LEFT JOIN host_tags ht ON h.host_id = ht.host_id
LEFT JOIN tags t ON ht.tag_id = t.tag_id
LEFT JOIN tag_groups tg ON t.tag_group_id = tg.tag_group_id

UNION ALL

-- Inherited network tags
SELECT 
    h.host_id,
    h.object_id,
    h.name AS host_name,
    h.status,
    n.name AS network_name,
    n.cidr AS network_cidr,
    b.name AS block_name,
    b.cidr AS block_cidr,
    l.location_name,
    t.name AS tag_name,
    tg.name AS tag_group_name,
    'network' AS tag_source
FROM hosts h
JOIN networks n ON h.network_id = n.network_id
JOIN blocks b ON n.block_id = b.block_id
JOIN locations l ON b.location_id = l.location_id
LEFT JOIN network_tags nt ON n.network_id = nt.network_id
LEFT JOIN tags t ON nt.tag_id = t.tag_id
LEFT JOIN tag_groups tg ON t.tag_group_id = tg.tag_group_id

UNION ALL

-- Inherited block tags
SELECT 
    h.host_id,
    h.object_id,
    h.name AS host_name,
    h.status,
    n.name AS network_name,
    n.cidr AS network_cidr,
    b.name AS block_name,
    b.cidr AS block_cidr,
    l.location_name,
    t.name AS tag_name,
    tg.name AS tag_group_name,
    'block' AS tag_source
FROM hosts h
JOIN networks n ON h.network_id = n.network_id
JOIN blocks b ON n.block_id = b.block_id
JOIN locations l ON b.location_id = l.location_id
LEFT JOIN block_tags bt ON b.block_id = bt.block_id
LEFT JOIN tags t ON bt.tag_id = t.tag_id
LEFT JOIN tag_groups tg ON t.tag_group_id = tg.tag_group_id;