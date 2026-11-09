from collections import defaultdict
from .base import IAnalyticsStrategy
from smartretail.core.domain import AnalyticsResult

class AnomalyDetectionStrategy(IAnalyticsStrategy):
    """Accumulate compact store/day metrics and report explainable alerts."""
    def __init__(self):
        super().__init__()
        self.daily = defaultdict(lambda: {'sales': 0, 'sale_units': 0, 'return_units': 0})
        self.alerts = []
        self.discount_spikes = 0

    def consume(self, records):
        super().consume(records)
        for record in records:
            day = record.transaction_datetime.date()
            metrics = self.daily[(record.store_id, day)]
            if record.is_return:
                metrics['return_units'] += abs(record.quantity)
            else:
                metrics['sales'] += record.total_amount
                metrics['sale_units'] += record.quantity
            if record.discount_percent is not None and record.discount_percent > 40:
                self.discount_spikes += 1
                self.alerts.append({'type':'Extreme discount','store_id':record.store_id,'date':str(day),
                                    'observed':f'{record.discount_percent}%','threshold':'> 40%'})

    def build_result(self):
        by_store = defaultdict(list)
        for (store, day), values in self.daily.items(): by_store[store].append((day, values))
        for store, days in by_store.items():
            days.sort(key=lambda item:item[0])
            for index, (day, values) in enumerate(days):
                history=[float(item[1]['sales']) for item in days[max(0,index-7):index] if item[1]['sales'] > 0]
                if history and float(values['sales']) < sum(history)/len(history)*0.5:
                    self.alerts.append({'type':'Sales drop','store_id':store,'date':str(day),
                                        'observed':str(values['sales']),'threshold':'below 50% of recent daily average'})
                if values['sale_units'] and values['return_units']/values['sale_units'] > 0.05:
                    rate=values['return_units']/values['sale_units']*100
                    self.alerts.append({'type':'High return rate','store_id':store,'date':str(day),
                                        'observed':f'{rate:.1f}%','threshold':'> 5%'})
        counts=defaultdict(int)
        for alert in self.alerts:counts[alert['type']]+=1
        alert_lines=[f"{a['type']} • {a['store_id']} • {a['date']} • {a['observed']} (limit {a['threshold']})" for a in self.alerts]
        return AnalyticsResult(type(self).__name__, {'records':self.records,'net_revenue':str(self.revenue),'alert_count':len(self.alerts),
            'discount_spikes':self.discount_spikes},
            {'alert_breakdown':[{'alert_type':key,'count':count} for key,count in sorted(counts.items())],
             'alert_details':self.alerts[:500]}, alerts=alert_lines)
