from datetime import datetime, date, timezone, timedelta
import math


def date_to_double(target_date: date):
    B = -13
    y = target_date.year
    m = target_date.month
    d = target_date.day
    JD = math.floor(365.25 * (y + 4716))+ math.floor(30.60001 * (m + 1)) + B + d - 1524.5
    return JD


def double_to_time(target_date: date, tz: int, time: float) -> datetime:
    t = time + 0.5
    t = (t - int(t)) * 24
    h = int(t)
    t = (t - h) * 60
    m = int(t)
    t = (t - m) * 60
    s = int(t)
    return datetime(target_date.year, target_date.month, target_date.day, h, m, s, tzinfo=timezone(timedelta(hours=tz)))


def sun_yellow(t):
    t = t + (32.0 * (t + 1.8) * (t + 1.8) - 20) / 86400.0 / 36525.0
    j = 48950621.66 + 6283319653.318 * t + 53 * t * t - 994 + 334166 * math.cos(4.669257 + 628.307585 * t) + 3489 * math.cos(4.6261 + 1256.61517 * t) + 2060.6 * math.cos(2.67823 + 628.307585 * t) * t
    return (j / 10000000)


def degree(ag):
    ag = ag % (2 * math.pi)
    if ag <= -math.pi:
        ag = ag + 2 * math.pi
    elif ag > math.pi:
        ag = ag - 2 * math.pi
    return ag


def calc_sunrise_time(sunrise_time: float, lat: float, lon: float, tz: float):
    RAD = 180 * 3600 / math.pi
    sunrise_time = sunrise_time - tz
    # 太阳黄经以及它的正余弦值
    t = sunrise_time / 36525
    j = sun_yellow(t)
    sin_j = math.sin(j)
    cos_j = math.cos(j)
    gst = 2 * math.pi * (0.779057273264 + 1.00273781191135 * sunrise_time) + (0.014506 + 4612.15739966 * t + 1.39667721 * t * t) / RAD
    E = (84381.406 - 46.836769 * t) / RAD  # 黄赤交角
    a = math.atan2(sin_j * math.cos(E), cos_j)  # 太阳赤经
    D = math.asin(math.sin(E) * sin_j)  # 太阳赤纬
    cosH0 = (math.sin(-50 * 60 / RAD) - math.sin(lat) * math.sin(D)) / (math.cos(lat) * math.cos(D))  # 日出的时角计算，地平线下50分
    cosH1 = (math.sin(-6 * 3600 / RAD) - math.sin(lat) * math.sin(D)) / (math.cos(lat) * math.cos(D))  # 天亮的时角计算，地平线下6度，若为航海请改为地平线下12度
    # 严格应当区分极昼极夜，本程序不算
    if cosH0 >= 1 or cosH0 <= -1:
        return -0.5, 0.0, 0.0  # 极昼
    H0 = -math.acos(cosH0)  # 升点时角（日出）若去掉负号 就是降点时角，也可以利用中天和升点计算
    H1 = -math.acos(cosH1)
    H = gst - lon - a  # 太阳时角
    midday_time = sunrise_time - degree(H) / math.pi / 2 + tz  # 中天时间
    dawn_time = sunrise_time - degree(H - H1) / math.pi / 2 + tz  # 天亮时间
    sunrise_time = sunrise_time - degree(H - H0) / math.pi / 2 + tz  # 日出时间
    return sunrise_time, dawn_time, midday_time


def calc_suntime(lat: float, lon: float, target_date: date, tz: int):
    # step 1
    lat = lat / 180 * math.pi
    lon = -lon / 180 * math.pi
    # step 2
    sunrise_time = date_to_double(target_date) - 2451544.5
    for _ in range(10):  # 逐步逼近法算10次
        sunrise_time, dawn_time, midday_time = calc_sunrise_time(sunrise_time, lat, lon, tz / 24)  # 逐步逼近法算10次
    sunset_time = midday_time + midday_time - sunrise_time
    twilight_time = midday_time + midday_time - dawn_time

    sunrise = double_to_time(target_date, tz, sunrise_time)
    dawn = double_to_time(target_date, tz, dawn_time)
    midday = double_to_time(target_date, tz, midday_time)
    sunset = double_to_time(target_date, tz, sunset_time)
    twilight = double_to_time(target_date, tz, twilight_time)
    return sunrise, sunset, midday, dawn, twilight


def main():
    sunrise_time, sunset_time, midday_time, dawn_time, twilight_time = calc_suntime(32.0603, 118.7969, date(2018, 12, 5), 8)
    print(f"日出时间：{sunrise_time.strftime('%H:%M:%S')}")
    print(f"日落时间：{sunset_time.strftime('%H:%M:%S')}")
    print(f"日中时间：{midday_time.strftime('%H:%M:%S')}")
    print(f"天亮时间：{dawn_time.strftime('%H:%M:%S')}")
    print(f"天黑时间：{twilight_time.strftime('%H:%M:%S')}")


if __name__ == '__main__':
    main()
