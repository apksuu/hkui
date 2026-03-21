import { getCacheRecord, setCacheRecord } from '../storage.js';

const WEATHER_CACHE_TTL = 1000 * 60 * 15;

function isFresh(record) {
  return record && Date.now() - record.savedAt < WEATHER_CACHE_TTL;
}

export async function searchCity(city) {
  const cacheKey = `geo:${city.toLowerCase()}`;
  const cached = getCacheRecord(cacheKey);
  if (isFresh(cached)) return cached.data;

  const url = new URL('https://geocoding-api.open-meteo.com/v1/search');
  url.searchParams.set('name', city);
  url.searchParams.set('count', '5');
  url.searchParams.set('language', 'en');
  url.searchParams.set('format', 'json');

  const response = await fetch(url);
  if (!response.ok) throw new Error('城市查询失败');
  const json = await response.json();
  setCacheRecord(cacheKey, { savedAt: Date.now(), data: json });
  return json;
}

export async function getForecastByCoords(latitude, longitude) {
  const cacheKey = `weather:${latitude.toFixed(3)},${longitude.toFixed(3)}`;
  const cached = getCacheRecord(cacheKey);
  if (isFresh(cached)) return cached.data;

  const url = new URL('https://api.open-meteo.com/v1/forecast');
  url.searchParams.set('latitude', String(latitude));
  url.searchParams.set('longitude', String(longitude));
  url.searchParams.set('current', 'temperature_2m,apparent_temperature,wind_speed_10m,relative_humidity_2m,weather_code');
  url.searchParams.set('daily', 'temperature_2m_max,temperature_2m_min,precipitation_probability_max');
  url.searchParams.set('timezone', 'auto');
  url.searchParams.set('forecast_days', '3');

  const response = await fetch(url);
  if (!response.ok) throw new Error('天气请求失败');
  const json = await response.json();
  setCacheRecord(cacheKey, { savedAt: Date.now(), data: json });
  return json;
}

export function getCurrentLocation() {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error('当前浏览器不支持定位'));
      return;
    }
    navigator.geolocation.getCurrentPosition(
      position => resolve(position.coords),
      error => reject(error),
      { enableHighAccuracy: false, timeout: 10000, maximumAge: 600000 }
    );
  });
}

export function weatherCodeLabel(code) {
  const map = {
    0: '晴朗',
    1: '大体晴朗',
    2: '局部多云',
    3: '阴天',
    45: '有雾',
    48: '冻雾',
    51: '小毛雨',
    53: '毛雨',
    55: '强毛雨',
    61: '小雨',
    63: '中雨',
    65: '大雨',
    71: '小雪',
    73: '中雪',
    75: '大雪',
    80: '阵雨',
    95: '雷暴'
  };
  return map[code] || `代码 ${code}`;
}
