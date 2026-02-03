#!/bin/bash

echo "================================"
echo "🧪 运行所有测试"
echo "================================"
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试计数
TOTAL=0
PASSED=0
FAILED=0

# 运行单个测试
run_test() {
    local test_file=$1
    local test_name=$2
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "运行: $test_name"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    TOTAL=$((TOTAL + 1))
    
    if python3 -B "$test_file"; then
        echo -e "${GREEN}✅ $test_name 通过${NC}"
        PASSED=$((PASSED + 1))
        return 0
    else
        echo -e "${RED}❌ $test_name 失败${NC}"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

# 单元测试
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📦 单元测试"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

run_test "tests/unit/test_1_hivision_core.py" "1. HivisionIDPhotos 核心功能"
run_test "tests/unit/test_2_tool_output.py" "2. 工具输出格式"
run_test "tests/unit/test_3_image_path_extraction.py" "3. IMAGE_PATH 提取逻辑"

# 集成测试
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔗 集成测试"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

run_test "tests/integration/test_4_agent_tool_call.py" "4. Agent 工具调用"
run_test "tests/integration/test_5_gradio_display.py" "5. Gradio 图片显示"

# 总结
echo ""
echo "================================"
echo "📊 测试总结"
echo "================================"
echo -e "总计: $TOTAL"
echo -e "${GREEN}通过: $PASSED${NC}"
echo -e "${RED}失败: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 所有测试通过！${NC}"
    exit 0
else
    echo -e "${RED}❌ 有 $FAILED 个测试失败${NC}"
    exit 1
fi
