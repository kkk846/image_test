import os
import json
from datetime import datetime
from typing import Dict, List
from jinja2 import Template


class ReportGenerator:
    def __init__(self, config: dict):
        self.config = config
        self.reports_dir = config['output']['reports_dir']
        self._ensure_reports_dir()

    def _ensure_reports_dir(self):
        os.makedirs(self.reports_dir, exist_ok=True)

    def generate_report(self, test_results: Dict, output_name: str = None) -> str:
        if output_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_name = f"test_report_{timestamp}.html"
        
        output_path = os.path.join(self.reports_dir, output_name)
        
        html_content = self._render_template(test_results)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"报告已生成: {output_path}")
        return output_path

    def _render_template(self, test_results: Dict) -> str:
        template_str = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>图像质量测试报告</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Microsoft YaHei', 'PingFang SC', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 15px 50px rgba(0,0,0,0.15);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.8em;
            margin-bottom: 15px;
            font-weight: 600;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        
        .header .subtitle {
            font-size: 1.2em;
            opacity: 0.95;
            margin-bottom: 10px;
        }
        
        .header .device-info {
            font-size: 1em;
            opacity: 0.85;
            margin-top: 15px;
            padding: 10px 20px;
            background: rgba(255,255,255,0.15);
            border-radius: 8px;
            display: inline-block;
        }
        
        .summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 25px;
            padding: 40px 30px;
            background: #f8f9fa;
        }
        
        .summary-card {
            background: white;
            padding: 25px;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .summary-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.12);
        }
        
        .summary-card h3 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 0.95em;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 600;
        }
        
        .summary-card .value {
            font-size: 2.5em;
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        }
        
        .summary-card .unit {
            font-size: 0.9em;
            color: #666;
        }
        
        .summary-card.pass .value {
            color: #28a745;
        }
        
        .summary-card.fail .value {
            color: #dc3545;
        }
        
        .content {
            padding: 40px 30px;
        }
        
        .section {
            margin-bottom: 50px;
        }
        
        .section h2 {
            color: #667eea;
            margin-bottom: 25px;
            padding-bottom: 15px;
            border-bottom: 3px solid #667eea;
            font-size: 1.8em;
            font-weight: 600;
        }
        
        .test-item {
            background: #f8f9fa;
            padding: 25px;
            border-radius: 10px;
            margin-bottom: 20px;
            border-left: 5px solid #667eea;
            transition: all 0.3s ease;
        }
        
        .test-item:hover {
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }
        
        .test-item.pass {
            border-left-color: #28a745;
            background: linear-gradient(to right, #f0fff4, #f8f9fa);
        }
        
        .test-item.fail {
            border-left-color: #dc3545;
            background: linear-gradient(to right, #fff5f5, #f8f9fa);
        }
        
        .test-item h3 {
            margin-bottom: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 1.3em;
            color: #333;
        }
        
        .test-item .badge {
            padding: 8px 20px;
            border-radius: 25px;
            font-size: 0.85em;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .test-item.pass .badge {
            background: linear-gradient(135deg, #28a745, #20c997);
            color: white;
            box-shadow: 0 2px 8px rgba(40, 167, 69, 0.3);
        }
        
        .test-item.fail .badge {
            background: linear-gradient(135deg, #dc3545, #c82333);
            color: white;
            box-shadow: 0 2px 8px rgba(220, 53, 69, 0.3);
        }
        
        .test-item .description {
            color: #666;
            margin-bottom: 15px;
            font-style: italic;
        }
        
        .test-item .details {
            margin-top: 20px;
            padding-top: 20px;
            border-top: 2px solid #dee2e6;
        }
        
        .test-item .detail-row {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #e9ecef;
            font-size: 1em;
        }
        
        .test-item .detail-row:last-child {
            border-bottom: none;
        }
        
        .test-item .detail-label {
            font-weight: 600;
            color: #555;
        }
        
        .test-item .detail-value {
            color: #333;
            font-family: 'Courier New', monospace;
        }
        
        .test-item .detail-value.good {
            color: #28a745;
            font-weight: bold;
        }
        
        .test-item .detail-value.bad {
            color: #dc3545;
            font-weight: bold;
        }
        
        .image-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 25px;
            margin-top: 25px;
        }
        
        .image-card {
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }
        
        .image-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 8px 30px rgba(0,0,0,0.15);
        }
        
        .image-card img {
            width: 100%;
            height: 220px;
            object-fit: cover;
            display: block;
        }
        
        .image-card .info {
            padding: 20px;
        }
        
        .image-card .info h4 {
            margin-bottom: 8px;
            color: #333;
            font-size: 1.1em;
        }
        
        .image-card .info p {
            font-size: 0.9em;
            color: #666;
            margin: 5px 0;
        }
        
        .footer {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .footer p {
            margin: 5px 0;
            opacity: 0.9;
        }
        
        .progress-section {
            margin-top: 30px;
            padding: 25px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        }
        
        .progress-item {
            margin-bottom: 20px;
        }
        
        .progress-item:last-child {
            margin-bottom: 0;
        }
        
        .progress-label {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            font-weight: 600;
        }
        
        .progress-bar {
            width: 100%;
            height: 12px;
            background: #e9ecef;
            border-radius: 6px;
            overflow: hidden;
        }
        
        .progress-bar .fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            transition: width 0.5s ease;
            border-radius: 6px;
        }
        
        .progress-bar .fill.success {
            background: linear-gradient(90deg, #28a745, #20c997);
        }
        
        .progress-bar .fill.warning {
            background: linear-gradient(90deg, #ffc107, #fd7e14);
        }
        
        .progress-bar .fill.danger {
            background: linear-gradient(90deg, #dc3545, #c82333);
        }
        
        .recommendations {
            margin-top: 30px;
            padding: 25px;
            background: linear-gradient(135deg, #fff3cd, #ffeeba);
            border-radius: 12px;
            border-left: 5px solid #ffc107;
        }
        
        .recommendations h4 {
            color: #856404;
            margin-bottom: 15px;
            font-size: 1.2em;
        }
        
        .recommendations ul {
            list-style: none;
            padding-left: 0;
        }
        
        .recommendations li {
            padding: 8px 0;
            padding-left: 25px;
            position: relative;
        }
        
        .recommendations li:before {
            content: "•";
            position: absolute;
            left: 0;
            color: #ffc107;
            font-weight: bold;
            font-size: 1.2em;
        }
        
        @media (max-width: 768px) {
            .header h1 {
                font-size: 2em;
            }
            
            .summary {
                grid-template-columns: 1fr;
            }
            
            .content {
                padding: 20px 15px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📸 图像质量测试报告</h1>
            <p class="subtitle">自动化图像质量评估系统</p>
            <div class="device-info">
                <strong>设备:</strong> {{ test_info.device_model }} 
                | <strong>制造商:</strong> {{ test_info.manufacturer }} 
                | <strong>Android版本:</strong> {{ test_info.android_version }}
            </div>
        </div>
        
        <div class="summary">
            <div class="summary-card {% if pass_rate >= 80 %}pass{% elif pass_rate >= 60 %}{% else %}fail{% endif %}">
                <h3>总通过率</h3>
                <div class="value">{{ "%.1f"|format(pass_rate) }}%</div>
                <div class="unit">测试通过率</div>
            </div>
            <div class="summary-card">
                <h3>总测试项</h3>
                <div class="value">{{ total_tests }}</div>
                <div class="unit">测试项目总数</div>
            </div>
            <div class="summary-card pass">
                <h3>✓ 通过</h3>
                <div class="value">{{ passed_tests }}</div>
                <div class="unit">测试通过数量</div>
            </div>
            <div class="summary-card fail">
                <h3>✗ 失败</h3>
                <div class="value">{{ total_tests - passed_tests }}</div>
                <div class="unit">测试失败数量</div>
            </div>
        </div>
        
        <div class="content">
            <div class="section">
                <h2>📊 测试进度概览</h2>
                <div class="progress-section">
                    <div class="progress-item">
                        <div class="progress-label">
                            <span>图像质量测试</span>
                            <span>{{ quality_pass_count }}/{{ quality_total_count }}</span>
                        </div>
                        <div class="progress-bar">
                            <div class="fill {% if quality_pass_rate >= 80 %}success{% elif quality_pass_rate >= 60 %}warning{% else %}danger{% endif %}" 
                                 style="width: {{ quality_pass_rate }}%"></div>
                        </div>
                    </div>
                    <div class="progress-item">
                        <div class="progress-label">
                            <span>清晰度测试</span>
                            <span>{{ sharpness_pass_count }}/{{ sharpness_total_count }}</span>
                        </div>
                        <div class="progress-bar">
                            <div class="fill {% if sharpness_pass_rate >= 80 %}success{% elif sharpness_pass_rate >= 60 %}warning{% else %}danger{% endif %}" 
                                 style="width: {{ sharpness_pass_rate }}%"></div>
                        </div>
                    </div>
                    <div class="progress-item">
                        <div class="progress-label">
                            <span>噪声检测</span>
                            <span>{{ noise_pass_count }}/{{ noise_total_count }}</span>
                        </div>
                        <div class="progress-bar">
                            <div class="fill {% if noise_pass_rate >= 80 %}success{% elif noise_pass_rate >= 60 %}warning{% else %}danger{% endif %}" 
                                 style="width: {{ noise_pass_rate }}%"></div>
                        </div>
                    </div>
                    <div class="progress-item">
                        <div class="progress-label">
                            <span>色彩分析</span>
                            <span>{{ color_pass_count }}/{{ color_total_count }}</span>
                        </div>
                        <div class="progress-bar">
                            <div class="fill {% if color_pass_rate >= 80 %}success{% elif color_pass_rate >= 60 %}warning{% else %}danger{% endif %}" 
                                 style="width: {{ color_pass_rate }}%"></div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>🎨 图像质量分析</h2>
                {% for test in quality_tests %}
                <div class="test-item {% if test.pass %}pass{% else %}fail{% endif %}">
                    <h3>
                        {{ test.name }}
                        <span class="badge">{% if test.pass %}✓ 通过{% else %}✗ 失败{% endif %}</span>
                    </h3>
                    <p class="description">{{ test.description }}</p>
                    <div class="details">
                        {% for detail in test.details %}
                        <div class="detail-row">
                            <span class="detail-label">{{ detail.label }}</span>
                            <span class="detail-value">{{ detail.value }}</span>
                        </div>
                        {% endfor %}
                    </div>
                </div>
                {% endfor %}
            </div>
            
            <div class="section">
                <h2>🔍 清晰度测试</h2>
                {% for test in sharpness_tests %}
                <div class="test-item {% if test.pass %}pass{% else %}fail{% endif %}">
                    <h3>
                        {{ test.name }}
                        <span class="badge">{% if test.pass %}✓ 通过{% else %}✗ 失败{% endif %}</span>
                    </h3>
                    <p class="description">{{ test.description }}</p>
                    <div class="details">
                        {% for detail in test.details %}
                        <div class="detail-row">
                            <span class="detail-label">{{ detail.label }}</span>
                            <span class="detail-value">{{ detail.value }}</span>
                        </div>
                        {% endfor %}
                    </div>
                </div>
                {% endfor %}
            </div>
            
            <div class="section">
                <h2>📡 噪声检测</h2>
                {% for test in noise_tests %}
                <div class="test-item {% if test.pass %}pass{% else %}fail{% endif %}">
                    <h3>
                        {{ test.name }}
                        <span class="badge">{% if test.pass %}✓ 通过{% else %}✗ 失败{% endif %}</span>
                    </h3>
                    <p class="description">{{ test.description }}</p>
                    <div class="details">
                        {% for detail in test.details %}
                        <div class="detail-row">
                            <span class="detail-label">{{ detail.label }}</span>
                            <span class="detail-value">{{ detail.value }}</span>
                        </div>
                        {% endfor %}
                    </div>
                </div>
                {% endfor %}
            </div>
            
            <div class="section">
                <h2>🌈 色彩分析</h2>
                {% for test in color_tests %}
                <div class="test-item {% if test.pass %}pass{% else %}fail{% endif %}">
                    <h3>
                        {{ test.name }}
                        <span class="badge">{% if test.pass %}✓ 通过{% else %}✗ 失败{% endif %}</span>
                    </h3>
                    <p class="description">{{ test.description }}</p>
                    <div class="details">
                        {% for detail in test.details %}
                        <div class="detail-row">
                            <span class="detail-label">{{ detail.label }}</span>
                            <span class="detail-value">{{ detail.value }}</span>
                        </div>
                        {% endfor %}
                    </div>
                </div>
                {% endfor %}
            </div>
            
            <div class="section">
                <h2>🖼️ 测试图像</h2>
                <div class="image-grid">
                    {% for image in test_images %}
                    <div class="image-card">
                        <img src="{{ image.path }}" alt="{{ image.name }}">
                        <div class="info">
                            <h4>{{ image.name }}</h4>
                            <p><strong>尺寸:</strong> {{ image.size }}</p>
                            <p><strong>路径:</strong> {{ image.path }}</p>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
            
            {% if recommendations %}
            <div class="section">
                <h2>💡 优化建议</h2>
                <div class="recommendations">
                    <h4>根据测试结果，我们建议：</h4>
                    <ul>
                        {% for rec in recommendations %}
                        <li>{{ rec }}</li>
                        {% endfor %}
                    </ul>
                </div>
            </div>
            {% endif %}
        </div>
        
        <div class="footer">
            <p><strong>报告生成时间:</strong> {{ test_info.timestamp }}</p>
            <p><strong>图像质量自动化测试工具</strong> v2.0 | 专为影像测试岗位设计</p>
            <p style="margin-top: 10px; font-size: 0.85em;">© 2024 图像质量自动化测试系统</p>
        </div>
    </div>
</body>
</html>
        """
        
        template = Template(template_str)
        return template.render(**test_results)
