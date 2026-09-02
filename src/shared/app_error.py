from dataclasses import dataclass

@dataclass
class AppError(Exception):
    component: str
    type: str
    code: str
    message: str

    @property
    def full_code(self) -> str:
        return f"{self.component}-{self.type}-{self.code}"

    def __post_init__(self) -> None:
        Exception.__init__(self, f"Error in '{self.component}' with type '{self.type}' and code '{self.code}': {self.message}")

    def to_dict(self) -> dict[str, str]:
        return {
            "component": self.component,
            "type": self.type,
            "code": self.code,
            "message": self.message,
            "full_code": self.full_code
        }