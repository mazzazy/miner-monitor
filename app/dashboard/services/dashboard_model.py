from app.dashboard.services.hashrate_formatter import HashrateFormatter

class DashboardModel:

    @staticmethod
    def from_api(workers):

        rows = []

        for name, info in workers.items():

            rows.append({

                "Worker": name,

                "Status": info.get("state", "unknown"),

                "5m TH/s": HashrateFormatter.gh_to_th(
                    info.get("hash_rate_5m", 0)
                    
                ),

                "60m TH/s": HashrateFormatter.gh_to_th(
                    info.get("hash_rate_60m", 0)
                    
                ),

                "24h TH/s": HashrateFormatter.gh_to_th(
                    info.get("hash_rate_24h", 0)
                    
                ),

                "Last Share": info.get("last_share")
            })

        return rows