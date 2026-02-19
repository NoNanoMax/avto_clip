# from sqlalchemy.orm import decl_base, Mapped, relationship
# from sqlalchemy import String, Text, DateTime, ForeignKey, func

# Base = decl_base()

# class Ad(Base):

#     __tablename__ = "ads"

#     id: Mapped[str] = mapped_column(String, primary_key=True)
#     description: Mapped[str | None] = mapped_column(Text, nullable=True)
#     meta_json: Mapped[str | None] = mapped_column(Text, nullable=True)  

#     created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
#     updated_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

#     photos: Mapped[list["Photo"]] = relationship(back_populates="ad", cascade="all, delete-orphan")

# class Photo(Base):

#     __tablename__ = "photos"

#     id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
#     ad_id: Mapped[str] = mapped_column(ForeignKey("ads.id"), index=True)

#     source_url: Mapped[str] = mapped_column(Text)
#     s3_key: Mapped[str] = mapped_column(Text)
#     s3_url: Mapped[str] = mapped_column(Text)

#     ad: Mapped[Ad] = relationship(back_populates="photos")


# if __name__ == "__main__":
#     import sqlalchemy
#     print(sqlalchemy.__version__)
