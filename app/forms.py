from flask_wtf import FlaskForm
from wtforms import HiddenField, IntegerField, PasswordField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Length, NumberRange, Regexp


class RegisterForm(FlaskForm):
    username = StringField(
        "아이디",
        validators=[
            DataRequired(),
            Length(min=3, max=30),
            Regexp(r"^[A-Za-z0-9_]+$", message="영문, 숫자, 밑줄만 사용할 수 있습니다."),
        ],
    )
    password = PasswordField("비밀번호", validators=[DataRequired(), Length(min=8, max=128)])
    confirm = PasswordField(
        "비밀번호 확인", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("가입")


class LoginForm(FlaskForm):
    username = StringField("아이디", validators=[DataRequired(), Length(max=30)])
    password = PasswordField("비밀번호", validators=[DataRequired(), Length(max=128)])
    submit = SubmitField("로그인")


class ProfileForm(FlaskForm):
    bio = TextAreaField("자기소개", validators=[Length(max=300)])
    submit = SubmitField("저장")


class ProductForm(FlaskForm):
    title = StringField("상품명", validators=[DataRequired(), Length(min=1, max=100)])
    description = TextAreaField("설명", validators=[DataRequired(), Length(min=1, max=2000)])
    price = IntegerField("가격", validators=[DataRequired(), NumberRange(min=1, max=100000000)])
    status = SelectField(
        "상태",
        choices=[("selling", "판매 중"), ("reserved", "예약 중"), ("sold", "판매 완료")],
    )
    submit = SubmitField("저장")


class MessageForm(FlaskForm):
    content = TextAreaField("메시지", validators=[DataRequired(), Length(min=1, max=1000)])
    submit = SubmitField("보내기")


class ReportForm(FlaskForm):
    target_type = SelectField("대상", choices=[("user", "사용자"), ("product", "상품")])
    target_id = IntegerField("대상 번호", validators=[DataRequired(), NumberRange(min=1)])
    reason = TextAreaField("신고 사유", validators=[DataRequired(), Length(min=5, max=500)])
    submit = SubmitField("신고")


class TransferForm(FlaskForm):
    receiver = StringField("받는 사용자", validators=[DataRequired(), Length(min=3, max=30)])
    amount = IntegerField("금액", validators=[DataRequired(), NumberRange(min=1, max=100000000)])
    password = PasswordField("현재 비밀번호", validators=[DataRequired(), Length(max=128)])
    idempotency_key = HiddenField(validators=[DataRequired(), Length(min=16, max=64)])
    submit = SubmitField("송금")
