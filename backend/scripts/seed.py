"""数据库初始化 + 种子数据。"""

from __future__ import annotations

import sys
from pathlib import Path

# 把 backend/ 加到 sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.security import hash_password
from app.db.session import Base, SessionLocal, engine
from app.models import (
    Department, Notification, Position, PositionStatus, Resume, ResumeChannel,
    ResumeSource, Role, User,
)


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(User).count() > 0:
            print("数据库已有数据，跳过 seed")
            return

        # 用户（密码统一为 123456）
        pwd = hash_password("123456")
        users_data = [
            ("A0001", "管理员", "admin@corp.com", Role.ADMIN, "HR 平台"),
            ("D1001", "周明", "zhoumin@corp.com", Role.HRD, "算力事业部 HR"),
            ("H2087", "张敏", "zhangmin@corp.com", Role.HRBP, "算力训练平台部"),
            ("H3056", "郑燕", "zhengyan@corp.com", Role.HRBP, "硬件加速部"),
            ("S2001", "孙磊", "sunlei@corp.com", Role.SOCIAL_LEAD, "招聘中心"),
            ("X3001", "陈晨", "chenchen@corp.com", Role.CAMPUS_LEAD, "招聘中心"),
        ]
        for uid, name, email, role, dept in users_data:
            db.add(User(id=uid, name=name, email=email, hashed_password=pwd,
                       role=role, dept=dept, status="在职"))
        db.flush()

        # 部门
        depts_data = [
            ("d1", "算力训练平台部", "H2087", "李建国", "王浩,刘洋"),
            ("d2", "智算调度部", "H2087", "陈伟", "孙琳"),
            ("d3", "硬件加速部", "H3056", "黄强", "吴迪,周倩"),
            ("d4", "算力运营部", "H3056", "刘芳", "徐磊"),
        ]
        for did, name, hrbp, mgr, cadres in depts_data:
            db.add(Department(id=did, name=name, hrbp_id=hrbp, mgr=mgr, cadres=cadres))
        db.flush()

        # 岗位
        positions_data = [
            ("p1", "训练框架高级工程师", "社招", "P7–P8", "d1", PositionStatus.ON,
             ["负责大规模分布式训练框架研发与性能优化", "主导千卡级集群通信/显存优化"],
             ["CUDA 编程", "分布式训练", "精通 C/C++", "3 年以上经验"],
             ["CUDA", "分布式训练", "Megatron", "显存优化"],
             [{"t": "大规模工程落地", "w": 30}, {"t": "跨团队协作", "w": 25},
              {"t": "抗压稳定", "w": 25}, {"t": "技术深度", "w": 20}]),
            ("p2", "算力底软开发", "校招", "校招 A/B", "d1", PositionStatus.ON,
             ["参与算子/编译/运行时开发", "在导师带领下完成模块级研发"],
             ["扎实 C++/计算机基础", "了解 CUDA 或体系结构"],
             ["CUDA", "算子优化", "C++", "编译"],
             [{"t": "学习潜力", "w": 35}, {"t": "技术深度", "w": 25},
              {"t": "抗压稳定", "w": 20}, {"t": "责任心", "w": 20}]),
            ("p3", "算力调度算法工程师", "社招", "P6–P7", "d2", PositionStatus.ON,
             ["设计算力资源调度与编排算法", "优化集群利用率与排队时延"],
             ["熟悉 K8s/调度系统", "Go 或 C++", "大规模分布式经验"],
             ["Kubernetes", "调度", "Go", "分布式"],
             [{"t": "系统化思维", "w": 30}, {"t": "算法建模", "w": 25},
              {"t": "抗压稳定", "w": 25}, {"t": "跨团队协作", "w": 20}]),
            ("p4", "调度平台开发", "校招", "校招 A/B", "d2", PositionStatus.ON,
             ["参与调度平台后端开发", "支撑平台稳定运行"],
             ["Go/Java 基础", "了解后端与 K8s"],
             ["Go", "后端", "Kubernetes"],
             [{"t": "学习潜力", "w": 35}, {"t": "责任心", "w": 25},
              {"t": "系统化思维", "w": 20}, {"t": "抗压稳定", "w": 20}]),
            ("p5", "异构计算研发工程师", "社招", "P6–P8", "d3", PositionStatus.ON,
             ["负责 FPGA/ASIC 异构加速方案研发", "软硬协同优化关键算子"],
             ["FPGA/Verilog/RTL 经验", "理解体系结构"],
             ["FPGA", "Verilog", "RTL", "硬件加速"],
             [{"t": "软硬协同", "w": 30}, {"t": "技术深度", "w": 25},
              {"t": "抗压稳定", "w": 25}, {"t": "跨团队协作", "w": 20}]),
            ("p6", "算力运营/测试开发", "校招", "校招 B", "d4", PositionStatus.OFF,
             ["参与平台测试与运营保障", "编写自动化测试与监控"],
             ["Python 基础", "了解 Linux/网络"],
             ["Python", "自动化测试", "Linux"],
             [{"t": "责任心", "w": 35}, {"t": "学习潜力", "w": 25},
              {"t": "抗压稳定", "w": 20}, {"t": "跨团队协作", "w": 20}]),
        ]
        for pid, name, chan, level, dept_id, status, duties, must, kw, imp in positions_data:
            db.add(Position(
                id=pid, name=name, chan=chan, level=level, department_id=dept_id,
                status=status, duties=duties, must=must, keywords=kw, implicit=imp,
            ))
        db.flush()

        # 简历
        resumes_data = [
            ("r1", "刘振宇", ResumeChannel.SOCIAL, "训练框架高级工程师", "H2087", "d1",
             ResumeSource.IMPORT, None,
             ["CUDA", "分布式训练", "Megatron", "PyTorch"],
             ["大规模工程落地", "跨团队协作", "技术深度"], 90),
            ("r2", "林一帆", ResumeChannel.CAMPUS, "算力底软开发", "H2087", "d1",
             ResumeSource.IMPORT, None,
             ["CUDA", "算子优化", "C++"],
             ["学习潜力", "技术深度", "抗压稳定"], 80),
            ("r3", "周晓", ResumeChannel.SOCIAL, "算力调度算法工程师", "H2087", "d2",
             ResumeSource.RECOMMEND, "A0001",
             ["Go", "Kubernetes", "调度"],
             ["系统化思维", "跨团队协作"], 76),
            ("r4", "赵睿", ResumeChannel.CAMPUS, "算力运营/测试开发", "H3056", "d4",
             ResumeSource.IMPORT, None,
             ["Python", "深度学习"],
             ["责任心", "学习潜力"], 66),
            ("r5", "李娜", ResumeChannel.SOCIAL, "异构计算研发工程师", "H3056", "d3",
             ResumeSource.RECOMMEND, "H2087",
             ["FPGA", "Verilog", "RTL"],
             ["软硬协同", "技术深度"], 84),
            ("r6", "吴坤", ResumeChannel.SOCIAL, "异构计算研发工程师", "H3056", "d3",
             ResumeSource.IMPORT, None,
             ["CUDA", "HPC", "C++"],
             ["技术深度", "抗压稳定"], 78),
        ]
        for rid, name, chan, pos, owner, dept, src, by, kw, tr, exp in resumes_data:
            db.add(Resume(
                id=rid, name=name, chan=chan, pos=pos, owner_id=owner,
                current_dept_id=dept, source=src, by_user_id=by,
                keywords=kw, traits=tr, exp_base=exp,
            ))
        db.flush()

        # 通知
        db.add(Notification(
            id="m1", to_user_id="H2087", from_user_id="A0001",
            type="recommend", title="新简历推荐：周晓",
            content="锻炼干部 王浩 把 周晓 推荐到了你名下",
            resume_id="r3",
        ))
        db.add(Notification(
            id="m2", to_user_id="H2087", from_user_id="X3001",
            type="recommend", title="新简历推荐：林一帆",
            content="校招负责人 陈晨 把 林一帆 推荐到了你名下",
            resume_id="r2",
        ))

        db.commit()
        print("✅ 种子数据写入完成")
        print("   - 6 个用户（密码统一：123456）")
        print("   - 4 个部门")
        print("   - 6 个岗位")
        print("   - 6 份简历")
        print("   - 2 条通知")
    finally:
        db.close()


if __name__ == "__main__":
    seed()