<template>
    <div class="status-box">
        <h3>Real-time Reserve Margin: {{ data.reserve_percent }}%</h3>
        <h3>Remaining Reserve: {{ (data.reserve_w * 0.01).toFixed(2) }} GW</h3>
        <div :class="['indicator', data.indicator]"></div>
        <div v-if="location">
            <p>🌎{{ latDMS }},{{ lonDMS }}</p>
        </div>
        <div v-if="weatherInfo.weather">
            <p>Weather：{{ weatherInfo.weather.Weather }}</p>
            <p>Temperature：{{ weatherInfo.weather.AirTemperature}}℃</p>
            <p>RelativeHumidity：{{ weatherInfo.weather.RelativeHumidity }}%</p>
            <p>WindSpeed：{{ weatherInfo.weather.WindSpeed }} m/s</p>
        </div>
        <div>
            <h3>UPS Info</h3>
            <p>Battery Charge：{{ ups.battery_charge }}%</p>
            <p>Battery Runtime:{{ ups.battery_runtime}}s</p>
            <p>UPS status：{{ ups.ups_status }}</p>
            <p>Light：<span :style="{ color: getColor(ups.light)}">●</span></p>
            <p>UPS Load：{{ ups.ups_load }}%</p>
            <p>Input Voltage：{{ ups.input_voltage}}V</p>
            <p>Output Voltage：{{ ups.output_voltage }}V</p>
        </div>
    </div>
</template>

<script setup>
    import { ref, onMounted, onBeforeUnmount } from 'vue'
    import axios from 'axios'

    const data = ref({
        reserve_percent: 0,
        reserve_w: 0,
        indicator: 'green'
    })
    const fetchReserve = async () => {
        const res = await axios.get('http://localhost:8000/api/power_supply')
        data.value = res.data
    }
    onMounted(() => {
        fetchReserve()
        setInterval(fetchReserve, 600*1000)  // 每小時更新一次
    })

    const location = ref(null)
    const latDMS = ref('')
    const lonDMS = ref('')
    const weatherInfo = ref({})
    let intervalId = null

    function decimalToDMS(coord, posSymbol, negSymbol) {
        const absolute = Math.abs(coord)
        const degrees = Math.floor(absolute)
        const minutesFull = (absolute - degrees) * 60
        const minutes = Math.floor(minutesFull)
        const seconds = ((minutesFull - minutes) * 60).toFixed(1)
        const direction = coord >= 0 ? posSymbol : negSymbol
        return `${direction}${degrees} ${minutes}' ${seconds}"`
    }

    function getWeatherIcon(weather) {
        if (weather.includes("晴")) return "/icons/sunny.png"
        if (weather.includes("陰")) return "☁️"
        if (weather.includes("雨")) return "🌧️"
        return "❓"
    }

    async function fetchWeatherAndLocation() {
        const res = await fetch("https://ipinfo.io/json?token=dc087daf7de4e0")
        const data = await res.json()
        const [latStr, lonStr] = data.loc.split(",")
        const lat = parseFloat(latStr)
        const lon = parseFloat(lonStr)

        location.value = { lat, lon }
        latDMS.value = decimalToDMS(lat, 'N', 'S')
        lonDMS.value = decimalToDMS(lon, 'E', 'W')

        await fetch("http://localhost:8000/api/gps_location", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ lat, lon })
        })

        const weatherRes = await fetch("http://localhost:8000/api/weather", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ lat, lon })
        })
        weatherInfo.value = await weatherRes.json()
    }

    onMounted(async () => {
        await fetchWeatherAndLocation()
        intervalId = setInterval(fetchWeatherAndLocation, 1800 * 1000)
    })

    onBeforeUnmount(() => {
        if (intervalId) clearInterval(intervalId)
    })

    const ups = ref({
        battery_charge: 0,
        ups_status: '',
        light: 'green',
        battery_runtime: 0,
        ups_load: 0,
        input_voltage: 0,
        OUTput_voltage:0,
    })

    function getColor(light) {
        return {
            red: 'red',
            yellow: 'orange',
            green: 'green'
        }[light] || 'gray'
    }

    async function fetchUPS() {
        try {
            const res = await fetch('http://localhost:8000/api/ups')
            const data = await res.json()
            ups.value = data
        } catch (error) {
            console.error('UPS 查詢失敗：', error)
        }
    }

    let intervalId2 = null

    onMounted(() => {
        fetchUPS()                              
        intervalId2 = setInterval(fetchUPS,10*1000) 
    })

    onBeforeUnmount(() => {
        clearInterval(intervalId2)
    })

</script>
    

<style scoped>
    .status-box {
        text-align: center;
    }

    .indicator {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        margin: 20px auto;
    }

    .green {
        background-color: #4CAF50;
    }

    .yellow {
        background-color: #FFEB3B;
    }

    .orange {
        background-color: #FF9800;
    }

    .red {
        background-color: #F44336;
    }

    .black {
        background-color: #000;
    }
</style>
