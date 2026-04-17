class QuotaManager:
    @staticmethod
    def format_bytes(size):
        # 2**10 = 1024
        power = 2**10
        n = 0
        power_labels = {0 : 'B', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
        while size > power:
            size /= power
            n += 1
        return f"{size:.2f} {power_labels[n]}"

    @staticmethod
    def format_gb(size_in_bytes):
        gb = size_in_bytes / (1024 ** 3)
        return f"{gb:.2f}"

    @staticmethod
    def calculate_quota(quota_data):
        limit = quota_data.get("limit_bytes_total", 0)
        used = quota_data.get("bytes_total_used", 0)
        
        if limit == 0:
            return {
                "left_str": "Unlimited",
                "limit_str": "Unlimited",
                "percentage": 100,
                "is_unlimited": True
            }
            
        remain = max(0, limit - used)
        percentage = min(int((remain / limit) * 100), 100)
        
        return {
            "left_str": f"{QuotaManager.format_gb(remain)} GB",
            "limit_str": f"{QuotaManager.format_gb(limit)} GB",
            "percentage": percentage,
            "is_unlimited": False
        }
