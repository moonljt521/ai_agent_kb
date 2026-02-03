#!/bin/bash

echo "🔍 验证证件照 URL 修复"
echo "="
echo ""

# 1. 检查目录
echo "1️⃣ 检查 photos 目录..."
if [ -d "app/static/photos" ]; then
    echo "   ✅ 目录存在"
    photo_count=$(ls -1 app/static/photos/*.jpg 2>/dev/null | wc -l)
    echo "   📸 找到 $photo_count 张图片"
    
    if [ $photo_count -gt 0 ]; then
        echo "   示例文件:"
        ls -1 app/static/photos/*.jpg 2>/dev/null | head -3 | while read file; do
            echo "      - $(basename "$file")"
        done
    fi
else
    echo "   ❌ 目录不存在"
fi

echo ""

# 2. 检查 main.py 配置
echo "2️⃣ 检查 main.py 配置..."
if grep -q 'app.mount("/photos"' app/main.py; then
    echo "   ✅ /photos 路由已配置"
    echo "   配置内容:"
    grep -A 1 'app.mount("/photos"' app/main.py | sed 's/^/      /'
else
    echo "   ❌ /photos 路由未配置"
    echo "   需要添加:"
    echo '      app.mount("/photos", StaticFiles(directory="app/static/photos"), name="photos")'
fi

echo ""

# 3. 检查 index.html 配置
echo "3️⃣ 检查 index.html 配置..."
if grep -q 'const imageUrl = `/photos/' app/static/index.html; then
    echo "   ✅ 前端 URL 配置正确"
else
    echo "   ⚠️ 前端 URL 可能需要更新"
fi

echo ""

# 4. 提供测试命令
echo "4️⃣ 测试步骤:"
echo "   1. 启动服务:"
echo "      python -m uvicorn app.main:app --reload --port 5000"
echo ""
echo "   2. 测试图片访问（在另一个终端）:"
if [ $photo_count -gt 0 ]; then
    first_photo=$(ls -1 app/static/photos/*.jpg 2>/dev/null | head -1 | xargs basename)
    echo "      curl -I http://localhost:5000/photos/$first_photo"
fi
echo ""
echo "   3. 在浏览器中访问:"
echo "      http://localhost:5000"
echo ""
echo "   4. 生成证件照并查看是否显示"

echo ""
echo "="
echo "✅ 验证完成"
