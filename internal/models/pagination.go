package models

type PaginationQuery struct {
    Page  int `form:"page" binding:"min=1"`
    Limit int `form:"limit" binding:"min=1,max=100"`
}

func (p *PaginationQuery) GetOffset() int {
    return (p.GetPage() - 1) * p.GetLimit()
}

func (p *PaginationQuery) GetLimit() int {
    if p.Limit == 0 {
        p.Limit = 10
    }
    return p.Limit
}

func (p *PaginationQuery) GetPage() int {
    if p.Page == 0 {
        p.Page = 1
    }
    return p.Page
}