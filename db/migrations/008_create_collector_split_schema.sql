CREATE TABLE IF NOT EXISTS sync_requests (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    request_type VARCHAR(64) NOT NULL,
    dataset VARCHAR(64) NOT NULL,
    scope_json JSON NULL,
    priority INT NOT NULL DEFAULT 50,
    status VARCHAR(32) NOT NULL DEFAULT 'pending',
    requested_by VARCHAR(64) NOT NULL DEFAULT 'api',
    reason VARCHAR(255) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    claimed_at TIMESTAMP NULL,
    finished_at TIMESTAMP NULL,
    error_message TEXT NULL,
    KEY idx_sync_requests_status_priority (status, priority, created_at),
    KEY idx_sync_requests_type_status (request_type, status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS dataset_freshness (
    dataset VARCHAR(64) NOT NULL,
    scope_key VARCHAR(128) NOT NULL DEFAULT 'global',
    latest_data_date DATE NULL,
    last_success_at TIMESTAMP NULL,
    last_attempt_at TIMESTAMP NULL,
    status VARCHAR(32) NOT NULL,
    rows_count BIGINT NOT NULL DEFAULT 0,
    missing_count BIGINT NOT NULL DEFAULT 0,
    failed_count BIGINT NOT NULL DEFAULT 0,
    owner_job_type VARCHAR(64) NULL,
    summary_json JSON NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (dataset, scope_key),
    KEY idx_dataset_freshness_status (status, updated_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
