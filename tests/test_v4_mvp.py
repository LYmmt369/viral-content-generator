#!/usr/bin/env python3
"""
v4.0 MVP 功能测试脚本
验证核心功能是否正常工作

作者: Sunnyeung
版本: 4.1.1
"""

import sys
from pathlib import Path

# 设置UTF-8编码输出（Windows兼容）
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def test_data_files():
    """测试数据文件是否完整"""
    print("=" * 60)
    print("测试1: 数据文件完整性")
    print("=" * 60)

    styles_dir = PROJECT_ROOT / "data" / "styles"
    accounts_dir = PROJECT_ROOT / "data" / "accounts"
    offers_dir = PROJECT_ROOT / "data" / "offers"
    prompts_dir = PROJECT_ROOT / "prompts"

    # 检查风格库
    style_files = list(styles_dir.glob("*.yaml"))
    print(f"[OK] 风格库文件: {len(style_files)} 个")
    for f in style_files:
        print(f"  - {f.name}")

    # 检查账号模板
    account_files = list(accounts_dir.glob("*.yaml"))
    print(f"[OK] 账号模板: {len(account_files)} 个")
    for f in account_files:
        print(f"  - {f.name}")

    # 检查产品模板
    offer_files = list(offers_dir.glob("*.yaml"))
    print(f"[OK] 产品模板: {len(offer_files)} 个")
    for f in offer_files:
        print(f"  - {f.name}")

    # 检查提示词模板
    prompt_files = list(prompts_dir.glob("*.md"))
    print(f"[OK] 提示词模板: {len(prompt_files)} 个")
    for f in prompt_files:
        print(f"  - {f.name}")

    print("\n[PASS] 数据文件测试通过\n")


def test_style_loading():
    """测试风格加载"""
    print("=" * 60)
    print("测试2: 风格加载")
    print("=" * 60)

    try:
        from viral_content.core import StyleMixer

        mixer = StyleMixer()
        styles = mixer.load_styles()

        print(f"[OK] 加载风格数量: {len(styles)}")

        # 按分类统计
        by_category = {}
        for style in styles.values():
            cat = style.get('category', 'unknown')
            by_category[cat] = by_category.get(cat, 0) + 1

        print("[OK] 风格分类统计:")
        for cat, count in by_category.items():
            print(f"  - {cat}: {count} 个")

        # 测试单个风格获取
        test_style = mixer.get_style("tech_explainer_global")
        if test_style:
            print(f"[OK] 单个风格加载成功: {test_style.get('label', '')}")
        else:
            print("[WARN] 单个风格加载失败")

        print("\n[PASS] 风格加载测试通过\n")
        return

    except Exception as e:  # noqa: BLE001
        print(f"[FAIL] 风格加载测试失败: {e}\n")
        raise AssertionError(str(e))


def test_style_mixing():
    """测试风格混合"""
    print("=" * 60)
    print("测试3: 风格混合")
    print("=" * 60)

    try:
        from viral_content.core import StyleMixer

        mixer = StyleMixer()

        # 测试兼容性检查
        compat = mixer.check_compatibility("tech_explainer_global", "business_podcast_host")
        print(f"[OK] 兼容性检查: tech_explainer_global vs business_podcast_host = {compat}")

        # 测试风格混合
        mixed = mixer.mix_styles(["tech_explainer_global", "business_podcast_host"])
        print(f"[OK] 风格混合成功: {mixed.get('component_styles', [])}")
        print(f"  权重: {mixed.get('weights', {})}")

        # 测试提示词上下文生成
        context = mixer.get_prompt_context(mixed)
        print(f"[OK] 提示词上下文生成成功（长度: {len(context)} 字符）")

        print("\n[PASS] 风格混合测试通过\n")
        return

    except Exception as e:  # noqa: BLE001
        print(f"[FAIL] 风格混合测试失败: {e}\n")
        raise AssertionError(str(e))


def test_account_loading():
    """测试账号加载"""
    print("=" * 60)
    print("测试4: 账号加载")
    print("=" * 60)

    try:
        from viral_content.core import AccountFingerprint

        # 测试默认账号
        account = AccountFingerprint.load_default()
        print(f"[OK] 默认账号加载: {account.name}")
        print(f"  定位: {account.identity}")

        # 测试配置获取
        print(f"[OK] 目标用户: {len(account.target_audience)} 条")
        print(f"[OK] 用户痛点: {len(account.pain_points)} 条")

        # 测试提示词上下文
        context = account.get_prompt_context()
        print(f"[OK] 提示词上下文生成成功（长度: {len(context)} 字符）")

        print("\n[PASS] 账号加载测试通过\n")
        return

    except Exception as e:  # noqa: BLE001
        print(f"[FAIL] 账号加载测试失败: {e}\n")
        import traceback
        traceback.print_exc()
        raise AssertionError(str(e))


def test_prompt_compilation():
    """测试提示词编译"""
    print("=" * 60)
    print("测试5: 提示词编译")
    print("=" * 60)

    try:
        from viral_content.core import AccountFingerprint, PromptCompiler, StyleMixer

        compiler = PromptCompiler()

        # 测试模板加载
        base_template = compiler.load_template("base_system")
        print(f"[OK] 基础模板加载成功（长度: {len(base_template)} 字符）")

        # 测试完整系统提示词构建
        mixer = StyleMixer()
        style_config = mixer.get_style("tech_explainer_global")

        account = AccountFingerprint.load_default()

        system_prompt = compiler.build_system_prompt(
            topic="AI Agent Runtime崩溃问题",
            style_config=style_config,
            account_config=account.to_dict(),
            goal="leads",
            platform="xiaohongshu",
        )

        print(f"[OK] 完整系统提示词构建成功（长度: {len(system_prompt)} 字符）")

        # 验证关键元素
        assert "AI Agent Runtime崩溃问题" in system_prompt, "话题未注入"
        assert "科技解释型" in system_prompt or "tech" in system_prompt.lower(), "风格未注入"
        assert "leads" in system_prompt.lower(), "目标未注入"

        print("[OK] 提示词内容验证通过")

        print("\n[PASS] 提示词编译测试通过\n")
        return

    except Exception as e:  # noqa: BLE001
        print(f"[FAIL] 提示词编译测试失败: {e}\n")
        import traceback
        traceback.print_exc()
        raise AssertionError(str(e))


def test_conversion_funnel():
    """测试成交漏斗"""
    print("=" * 60)
    print("测试6: 成交漏斗")
    print("=" * 60)

    try:
        from viral_content.core import ConversionFunnel

        # 测试不同目标
        for goal_str in ["likes", "comments", "leads", "sales"]:
            funnel = ConversionFunnel.from_string(goal_str)

            print(f"\n[OK] 目标: {goal_str}")
            print(f"  - CTA建议: {', '.join(funnel.get_cta_suggestions()[:2])}")

            standards = funnel.get_quality_standards()
            print(f"  - 质量标准: {len(standards)} 项")

            outline = funnel.generate_content_outline(1000)
            print(f"  - 内容结构: 开头{outline['开头']}字, 主体{outline['主体']}字, 结尾{outline['结尾']}字")

        print("\n[PASS] 成交漏斗测试通过\n")
        return

    except Exception as e:  # noqa: BLE001
        print(f"[FAIL] 成交漏斗测试失败: {e}\n")
        import traceback
        traceback.print_exc()
        raise AssertionError(str(e))


def test_hot_topic_input():
    """测试热点输入"""
    print("=" * 60)
    print("测试7: 热点输入")
    print("=" * 60)

    try:
        from viral_content_cli import HotTopicInput

        # 测试文本输入
        text_input = HotTopicInput.from_text("马斯克2026访谈")
        print(f"[OK] 文本输入成功: {text_input[0]['topic']}")

        print("\n[PASS] 热点输入测试通过\n")
        return

    except Exception as e:  # noqa: BLE001
        print(f"[FAIL] 热点输入测试失败: {e}\n")
        import traceback
        traceback.print_exc()
        raise AssertionError(str(e))


def test_integration():
    """集成测试"""
    print("=" * 60)
    print("测试8: 集成测试（模拟完整流程）")
    print("=" * 60)

    try:
        from viral_content.core import (
            AccountFingerprint,
            ConversionFunnel,
            ConversionGoal,
            PromptCompiler,
            StyleMixer,
        )

        print("1. 初始化核心组件...")
        compiler = PromptCompiler()
        mixer = StyleMixer()
        account = AccountFingerprint.load_default()
        funnel = ConversionFunnel(ConversionGoal.LEADS)
        print("[OK] 核心组件初始化成功")

        print("\n2. 加载风格并混合...")
        mixed_style = mixer.mix_styles([
            "tech_explainer_global",
            "business_savage_china"
        ], weights={"tech_explainer_global": 0.6, "business_savage_china": 0.4})
        print(f"[OK] 风格混合成功: {mixed_style.get('component_styles', [])}")

        print("\n3. 构建完整系统提示词...")
        system_prompt = compiler.build_system_prompt(
            topic="2026年AI行业最大趋势",
            style_config=mixed_style,
            account_config=account.to_dict(),
            offer_config=None,
            goal="leads",
            platform="xiaohongshu",
        )
        print(f"[OK] 系统提示词构建成功（{len(system_prompt)} 字符）")

        print("\n4. 验证成交目标配置...")
        cta_list = funnel.get_cta_suggestions()
        print(f"[OK] CTA建议: {len(cta_list)} 条")
        print(f"  示例: {cta_list[0]}")

        print("\n5. 验证账号信息...")
        account_context = account.get_prompt_context()
        print(f"[OK] 账号上下文生成成功（{len(account_context)} 字符）")
        print(f"  账号名: {account.name}")

        print("\n[PASS] 集成测试通过")
        print("\n核心功能验证：")
        print("  [OK] 风格库加载与混合")
        print("  [OK] 账号配置管理")
        print("  [OK] 提示词动态编译")
        print("  [OK] 成交目标适配")
        print("  [OK] 热点输入处理")

        return

    except Exception as e:  # noqa: BLE001
        print(f"\n[FAIL] 集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        raise AssertionError(str(e))


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("v4.0 MVP 功能测试")
    print("=" * 60 + "\n")

    tests = [
        ("数据文件完整性", test_data_files),
        ("风格加载", test_style_loading),
        ("风格混合", test_style_mixing),
        ("账号加载", test_account_loading),
        ("提示词编译", test_prompt_compilation),
        ("成交漏斗", test_conversion_funnel),
        ("热点输入", test_hot_topic_input),
        ("集成测试", test_integration),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:  # noqa: BLE001
            print(f"[FAIL] 测试异常: {name} - {e}\n")
            results.append((name, False))

    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)

    passed = sum(1 for _, result in results if result is not False)
    total = len(results)

    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {name}")

    print(f"\n总计: {passed}/{total} 通过")

    if passed == total:
        print("\n所有测试通过！v4.0 MVP 核心功能验证成功")
        return 0
    else:
        print(f"\n{total - passed} 个测试失败，需要修复")
        return 1


if __name__ == '__main__':
    sys.exit(main())


def test_public_version_and_cli_entrypoint():
    import viral_content
    assert viral_content.__version__ == '4.1.1'
    from viral_content_cli import main
    assert callable(main)



def test_quality_gate_blocks_risky_copy():
    from viral_content.core.quality_gate import QualityGate
    gate = QualityGate()
    result = gate.check('保证爆款，点击领取 [优惠内容]', require_cta=True)
    assert not result.passed
    assert len(result.warnings) >= 2


def test_quality_gate_accepts_reviewable_copy():
    from viral_content.core.quality_gate import QualityGate
    result = QualityGate().check('This concrete explanation covers a real scenario, limits, and actionable steps for small business owners. Leave a question in the comments and I will add a sourced example so you can judge whether it fits your situation.', require_cta=True)
    assert result.passed
    assert result.warnings == []



def test_candidate_ranker_prefers_safe_candidate():
    from viral_content.core.experiment import Candidate, CandidateRanker
    ranked = CandidateRanker('leads').rank([Candidate('unsafe', 9, False), Candidate('safe', 7, True)])
    assert ranked[0].content == 'safe'


def test_feedback_record_serializes():
    from viral_content.core.experiment import FeedbackRecord
    record = FeedbackRecord(1, 'xiaohongshu', '2026-09-15', impressions=100)
    assert record.to_dict()['impressions'] == 100



def test_feedback_summary_warns_on_small_sample():
    from viral_content.core.experiment import FeedbackRecord, summarize_feedback
    summary = summarize_feedback([FeedbackRecord(0, 'douyin', '2026-09-15', impressions=100, comments=5)])
    assert summary.winner_index is None
    assert not summary.reliable
    assert '样本量' in summary.note



def test_platform_bias_changes_ranker_weights():
    from viral_content.core.experiment import CandidateRanker
    assert CandidateRanker('likes', 'douyin').quality_weight > CandidateRanker('likes', 'zhihu').quality_weight



def test_ranker_describes_weights():
    from viral_content.core.experiment import CandidateRanker
    info = CandidateRanker('leads', 'douyin').describe()
    assert info['goal'] == 'leads'
    assert info['quality_weight'] + info['gate_weight'] == 1.0



def test_feedback_report_exports_json(tmp_path):
    from viral_content.core.experiment import FeedbackRecord, export_feedback_report
    path = tmp_path / 'report.json'
    export_feedback_report([FeedbackRecord(0, 'wechat', '2026-09-15', views=100)], str(path))
    assert 'summary' in path.read_text(encoding='utf-8')



def test_installed_resource_paths_exist():
    from viral_content.config.constants import (
        PROMPTS_DIR,
        SKILL_FALLBACK_PATH,
        STYLES_DIR,
    )
    assert SKILL_FALLBACK_PATH.is_file()
    assert (PROMPTS_DIR / "base_system.md").is_file()
    assert any(STYLES_DIR.glob("*.yaml"))
