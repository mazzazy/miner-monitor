class HashrateFormatter:

    @staticmethod
    def gh_to_th(value):

        if value is None:
            return 0

        return round(float(value) / 1000, 2)

    @staticmethod
    def format_farm_hashrate(total_th):

        if total_th >= 1000:
            return f"{total_th / 1000:.2f} PH/s"

        return f"{total_th:.2f} TH/s"