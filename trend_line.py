from math import atan, degrees, fabs
import copy

class MinMaxPoint(object):
    # Klasa ma za zadanie obliczać ujemny indeks wartości minimum na giełdzie oraz wartości maksimum
    # stock_data - dane z giełdy w postaci listy n elementowej
    # step - krok o jaki ma liczyć linię trendu
    def __init__(self, stock_data, step):
        self.stock_data = stock_data
        self.step = step

    def minimum(self):
        minimum_index = None
        index_a = -self.step
        trend_up = TrendLine(short_data=self.stock_data, index_a=index_a, index_b=None)
        trend_up = trend_up.trend_line()[0]
        n = 1
        # Sprawdza, czy współczynnik a1 jest większy od 0 a co za tym idzie funkcja jest rosnąca.
        while trend_up > 0:
            index_a = - (self.step + self.step * n)
            index_b = - (self.step * n)
            trend_up = TrendLine(short_data=self.stock_data, index_a=index_a, index_b=index_b)
            trend_up = trend_up.trend_line()[0]
            if trend_up > 0:
                n += 1
            else:
                data = self.stock_data[-(self.step + self.step * n):-(self.step * (n - 1))]
                minimum = min(data)
                # Jeżeli wartość się powtarza, to index może się nie zgadzać, ponieważ zawsze zwracany jest pierwszy znaleziony index
                minimum_index = self.stock_data.index(minimum)
        return minimum_index

    def extreme(self, minimum_index):
        extreme_index = None
        index_a = minimum_index - self.step
        index_b = minimum_index
        trend_down = TrendLine(short_data=self.stock_data, index_a=index_a, index_b=index_b)
        trend_down = trend_down.trend_line()[0]
        n = 1
        while trend_down <= 0:
            index_a = (minimum_index - self.step * (n + 1))
            index_b = (minimum_index - self.step * n)
            # Sprawdza, czy index nie przekroczył wartości ujemnej
            if index_a > 0:
                trend_down = TrendLine(short_data=self.stock_data, index_a=index_a, index_b=index_b)
                trend_down = trend_down.trend_line()[0]
                if trend_down <= 0:
                    n += 1
                else:
                    # Jeżeli linia trendu jest dodatnia to znaczy, że algorytm znalazł przedział, w którym funkcja
                    # przyjmuje wartość minimum lokalnego
                    data = self.stock_data[
                           (minimum_index - self.step * (n + 1)):(minimum_index - self.step * (n - 1))]
                    maximum = max(data)
                    extreme_index = self.stock_data.index(maximum)
            else:
                data = self.stock_data[:self.step + 1]
                maximum = max(data)
                extreme_index = self.stock_data.index(maximum)
                return extreme_index
        return extreme_index


class CutData(object):
    # Klasa ma za zadanie zwrócić listę giełdową skróconą o wartości przed wartością maksymalną
    def __init__(self, stock_data, extreme):
        self.stock_data = stock_data
        self.max = extreme

    def short_data(self):
        pass


class TrendLine(object):
    def __init__(self, short_data, index_a=None, index_b=None):
        self.short_data = short_data
        self.index_a = index_a
        self.index_b = index_b

    def trend_line(self):
        # Zwraca współczynniki a1, a0 dla wzoru y = a1*t + a0
        if self.index_a or self.index_b is not None:
            data = copy.deepcopy(self.short_data[self.index_a:self.index_b])
        else:
            data = copy.deepcopy(self.short_data)

        sum_y = 0
        sum_e = 0
        sum_t_t2 = 0
        i = 1
        b = (len(data) + 1) / 2
        n = 0
        # Przekonwertowanie data = [y1, y2, y3, ..., yn] na [[y1], [y2], [y3], ..., [yn]]
        for y_t in data:
            data[n] = [y_t]
            n += 1

        for y_t in data:
            # Obliczenie sumy współczynników B = y_t
            sum_y += y_t[0]
            # Obliczenie współczynnika C = t - t~
            data[i - 1].append(int(i - b))
            # Obliczenie współczynnika D = C ** 2
            data[i - 1].append(int(data[i - 1][1] ** 2))
            # Obliczenie współczynnika E = B * C
            data[i - 1].append(data[i - 1][0] * data[i - 1][1])
            # Obliczenie sumy współczynników D
            sum_t_t2 += data[i - 1][2]
            # Obliczenie sumy współczynników E
            sum_e += data[i - 1][3]
            i += 1

        sum_y = round(sum_y, 1)

        # Obliczenie współczynników a1, a0
        a1 = sum_e / sum_t_t2
        a0 = (sum_y / len(data)) - (a1 * b)

        a1_a0 = [round(a1, 2), round(a0, 2)]
        return a1_a0


def angle(trend_1, trend_2):
    a1 = trend_1[0]
    a2 = trend_2[0]
    if a1 * a2 == -1:
        return 90
    else:
        tg_alpha = (a1 - a2)/(1 + a1 * a2)
        alpha = degrees(atan(tg_alpha))
        return fabs(alpha)


def table_all(table, step):
    min_max = MinMaxPoint(stock_data=table, step=step)
    # Algorytm liczy wartość minimum na liście poruszając się od końca do początku. Sprawdzane są tzw. (sub) linie trendu
    # obliczane dla liczby wartości podanej w argumencie step. Uwaga! Argument step przyjmuje wartości: step >=3

    minimum_index = min_max.minimum()
    maximum_index = min_max.extreme(minimum_index=minimum_index)

    trend_grow = TrendLine(short_data=table[minimum_index:]).trend_line()
    trend_drop = TrendLine(short_data=table[maximum_index:minimum_index + 1]).trend_line()

    table = table[maximum_index:]
    table_length = len(table)
    labels = [z + 1 for z in range(table_length)]

    trend_drop_table = [round(trend_drop[0] * n + trend_drop[1], 4) for n in range(minimum_index - maximum_index + 1)]

    for n in range(table_length - (minimum_index - maximum_index + 1)):
        trend_drop_table.append(None)

    trend_grow_table = []
    for n in range(minimum_index - maximum_index):
        trend_grow_table.append(None)

    for n in range(table_length - (minimum_index - maximum_index)):
        trend_grow_table.append(round(trend_grow[0] * n + trend_grow[1], 5))

    line_angle = angle(trend_drop, trend_grow)

    default_items = [labels, table, trend_drop_table, trend_grow_table, trend_drop, trend_grow, line_angle]

    return default_items
