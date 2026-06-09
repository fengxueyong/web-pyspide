CREATE DATABASE IF NOT EXISTS web_collector
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE web_collector;

-- 抓取任务表
CREATE TABLE IF NOT EXISTS t_scrap_task (
    id            INT             AUTO_INCREMENT PRIMARY KEY  COMMENT '抓取任务ID',
    website       VARCHAR(2048)   NOT NULL                    COMMENT '网址',
    website_hash  CHAR(32)        NOT NULL                    COMMENT '网址MD5，用于索引和去重',
    res_type      VARCHAR(64)     NOT NULL DEFAULT 'all'      COMMENT '资源类型：all-全部, text/article-文本/文章, pic-图片, doc-文档, audio-音频, video-视频',
    scrap_time    DATETIME                                    COMMENT '爬取时间',
    cancel_time   DATETIME                                    COMMENT '取消时间，可空',
    depth         INT             NOT NULL DEFAULT 1          COMMENT '抓取深度：1/2/3',
    link_follow   INT             NOT NULL DEFAULT 0          COMMENT '是否跟随链接：0-否, 1-是',
    save_method   VARCHAR(16)     NOT NULL DEFAULT 'download' COMMENT '保存方式：only_record-仅记录元数据, download-下载文件',
    status        VARCHAR(16)     NOT NULL DEFAULT 'running'  COMMENT '任务状态：running-运行中, finished-已完成, cancel-已取消',
    res_number  INT             NOT NULL DEFAULT 0          COMMENT '抓取资源数',
    extension     JSON                                      COMMENT '扩展字段，可空',
    INDEX idx_task_query (website_hash, res_type, depth, link_follow, save_method)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='抓取任务';

-- 资源表
CREATE TABLE IF NOT EXISTS t_resources (
    id            INT           AUTO_INCREMENT PRIMARY KEY  COMMENT '资源ID',
    scrap_task_id INT           NOT NULL                    COMMENT '抓取任务ID',
    website       VARCHAR(2048)   NOT NULL                  COMMENT '冗余字段，关联任务网址',
    res_link      TEXT                                      COMMENT '资源链接，可空',
    parent_link   TEXT          NOT NULL DEFAULT '-1'       COMMENT '父链接，-1表示第一层',
    res_type      VARCHAR(32)   NOT NULL                    COMMENT '资源类型：text/article-文本/文章, pic-图片, doc-文档, audio-音频, video-视频',
    object_id     VARCHAR(256)                              COMMENT 'MongoDB/MinIO 对象标识',
    res_size      BIGINT        NOT NULL DEFAULT 0          COMMENT '资源大小（字节）',
    create_time   DATETIME                                  COMMENT '创建时间',
    update_time   DATETIME                                  COMMENT '更新时间',
    extension     JSON                                      COMMENT '扩展字段，可空',
    INDEX idx_task_resource (scrap_task_id, res_link(255))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='抓取资源';


