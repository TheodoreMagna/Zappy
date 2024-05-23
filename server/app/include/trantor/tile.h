/*
** EPITECH PROJECT, 2024
** Zappy [WSL: Ubuntu]
** File description:
** tile header
*/

#pragma once

#include "trantor/common.h"
#include "trantor/item.h"

#define GET_ITEM(tl, tp) ((tl).items[(tp) - 1])
#define SET_ITEM(tl, tp, val) ((tl).items[(tp) - 1] = val)
#define HAS_ITEM(tl, tp) (GET_ITEM(tl, tp) > 0)
#define TAKE_ITEM(tl, tp) (GET_ITEM(tl, tp)--)
#define ADD_ITEM(tl, tp) (GET_ITEM(tl, tp)++)

typedef struct tile_s {
    quant_t items[7];
} tile_t;

void get_item_count(len_t width, len_t height, tile_t *quants);
item_t rand_item(tile_t *items_left, len_t tiles_left);
item_t take_rand_item(tile_t *tile);
quant_t get_total_items(tile_t *tile);
