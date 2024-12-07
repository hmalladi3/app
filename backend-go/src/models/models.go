package models

import (
	"time"

	"gorm.io/gorm"
)

type Account struct {
	gorm.Model
	Username string    `gorm:"unique;not null" json:"username"`
	Email    string    `gorm:"unique;not null" json:"email"`
	Password string    `gorm:"not null" json:"-"`
	Services []Service `gorm:"foreignKey:AccountID" json:"services,omitempty"`
	Reviews  []Review  `gorm:"foreignKey:ClientID" json:"reviews,omitempty"`
	Hashtags []Hashtag `gorm:"many2many:account_hashtags;" json:"hashtags,omitempty"`
}

type Service struct {
	gorm.Model
	Title       string    `gorm:"not null" json:"title"`
	Description string    `json:"description"`
	Price       int       `gorm:"not null" json:"price"` // in cents
	AccountID   uint      `gorm:"not null" json:"account_id"`
	Reviews     []Review  `json:"reviews,omitempty"`
	Account     Account   `json:"account,omitempty"`
	CreatedAt   time.Time `json:"created_at"`
	UpdatedAt   time.Time `json:"updated_at"`
}

type Review struct {
	gorm.Model
	Rating    int       `gorm:"not null;check:rating >= 1 AND rating <= 5" json:"rating"`
	Title     string    `gorm:"not null" json:"title"`
	Body      string    `json:"body"`
	ServiceID uint      `gorm:"not null" json:"service_id"`
	ClientID  uint      `gorm:"not null" json:"client_id"`
	Service   Service   `json:"service,omitempty"`
	Client    Account   `json:"client,omitempty"`
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
}

type Hashtag struct {
	gorm.Model
	Tag      string    `gorm:"unique;not null" json:"tag"`
	Accounts []Account `gorm:"many2many:account_hashtags;" json:"accounts,omitempty"`
}

type AccountHashtag struct {
	AccountID uint    `gorm:"primaryKey"`
	HashtagID uint    `gorm:"primaryKey"`
	Account   Account `json:"account,omitempty"`
	Hashtag   Hashtag `json:"hashtag,omitempty"`
}

// Request/Response models
type AccountCreate struct {
	Username string `json:"username" binding:"required"`
	Email    string `json:"email" binding:"required,email"`
	Password string `json:"password" binding:"required"`
}

type AccountUpdate struct {
	Username *string `json:"username,omitempty"`
	Email    *string `json:"email,omitempty"`
	Password *string `json:"password,omitempty"`
}

type ServiceCreate struct {
	Title       string `json:"title" binding:"required"`
	Description string `json:"description"`
	Price       int    `json:"price" binding:"required"`
}

type ReviewCreate struct {
	Rating int    `json:"rating" binding:"required,min=1,max=5"`
	Title  string `json:"title" binding:"required"`
	Body   string `json:"body"`
}

type LoginRequest struct {
	Username string `json:"username" binding:"required"`
	Password string `json:"password" binding:"required"`
}

type LoginResponse struct {
	AccountID uint   `json:"account_id"`
	Username  string `json:"username"`
	Token     string `json:"token"`
}
