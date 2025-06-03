from extensions import db

class User(db.Model):
    id = db.Column(db.String(20), primary_key=True)  # 学号/ID
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(255))  # 扩展长度以存储哈希密码
    role = db.Column(db.String(20), nullable=False)  # 角色: student, teacher, admin

    def __repr__(self):
        return f'<User {self.username}>'