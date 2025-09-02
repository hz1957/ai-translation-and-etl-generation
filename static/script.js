// static/script.js

document.addEventListener('DOMContentLoaded', function () {
    // 基于准备好的dom，初始化echarts实例
    const durationChart = echarts.init(document.getElementById('duration-chart'));

    // ECharts图表的基本配置
    const chartOption = {
        title: {
            text: '最近LLM调用耗时 (秒)'
        },
        tooltip: {
            trigger: 'axis'
        },
        xAxis: {
            type: 'category',
            data: [], // 将由API数据填充
            axisLabel: {
                formatter: function (value) {
                    // 格式化时间戳，只显示 时:分:秒
                    const date = new Date(value);
                    return [date.getHours(), date.getMinutes(), date.getSeconds()].map(n => n.toString().padStart(2, '0')).join(':');
                }
            }
        },
        yAxis: {
            type: 'value',
            name: '耗时 (s)'
        },
        series: [{
            data: [], // 将由API数据填充
            type: 'line',
            smooth: true,
            areaStyle: {}
        }]
    };

    // 更新仪表盘数据的函数
    async function updateDashboard() {
        try {
            // 注意：我们假设API路由被挂载在/api/model-platform下
            const response = await fetch('/api/model-platform/status');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const stats = await response.json();

            // 1. 更新统计卡片
            document.getElementById('total-calls').textContent = stats.total_calls;
            document.getElementById('success-rate').textContent = `${stats.success_rate.toFixed(2)}%`;
            document.getElementById('avg-duration').textContent = stats.average_duration.toFixed(2);
            document.getElementById('failed-calls').textContent = stats.failed_calls;
            document.getElementById('cache-size').textContent = stats.cache_size;

            // 2. 更新ECharts图表
            const chartData = stats.recent_traces.map(trace => ({
                value: trace.duration,
                name: trace.start_time
            })).reverse(); // 反转数组，让最新的数据显示在右边

            durationChart.setOption({
                xAxis: {
                    data: chartData.map(item => item.name)
                },
                series: [{
                    data: chartData.map(item => item.value)
                }]
            });

            // 3. 更新最近调用记录表格
            const tableBody = document.getElementById('traces-table');
            tableBody.innerHTML = ''; // 清空旧数据
            stats.recent_traces.forEach(trace => {
                const row = document.createElement('tr');
                const statusClass = trace.success ? 'success' : 'failure';
                
                row.innerHTML = `
                    <td>${new Date(trace.start_time).toLocaleString()}</td>
                    <td class="${statusClass}">${trace.success ? '成功' : '失败'}</td>
                    <td>${trace.duration.toFixed(2)}</td>
                    <td>${trace.error_message || 'N/A'}</td>
                `;
                tableBody.appendChild(row);
            });

        } catch (error) {
            console.error("无法获取监控数据:", error);
        }
    }

    // 页面加载时立即更新一次，之后每5秒刷新一次
    updateDashboard();
    setInterval(updateDashboard, 5000);

    // 应用初始配置
    durationChart.setOption(chartOption);
    // 监听窗口大小变化，使图表自适应
    window.addEventListener('resize', function() {
        durationChart.resize();
    });
});