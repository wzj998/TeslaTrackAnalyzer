def calculate_wheel_diameter(width_mm: float, aspect_ratio: float, rim_diameter_inch: float) -> float:
    """
    计算车轮外径(单位:毫米)
    
    参数:
        width_mm: float - 轮胎宽度(毫米)
        aspect_ratio: float - 扁平比(百分比)
        rim_diameter_inch: float - 轮圈内径(英寸)
    
    返回:
        float: 车轮外径(毫米)
    """
    # 将轮圈内径从英寸转换为毫米
    rim_diameter_mm = rim_diameter_inch * 25.4
    
    # 计算侧壁高度 (轮胎宽度 * 扁平比%)
    sidewall_height = width_mm * (aspect_ratio / 100)
    
    # 计算总直径 = 轮圈直径 + (2 * 侧壁高度)
    total_diameter = rim_diameter_mm + (2 * sidewall_height)
    
    # return round(total_diameter, 2)
    return total_diameter
